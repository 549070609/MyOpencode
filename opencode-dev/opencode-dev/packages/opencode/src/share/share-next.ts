import { Bus } from "@/bus"
import { Config } from "@/config/config"
import { ulid } from "ulid"
import { Provider } from "@/provider/provider"
import { Session } from "@/session"
import { MessageV2 } from "@/session/message-v2"
import { Storage } from "@/storage/storage"
import { Log } from "@/util/log"
import { Flag } from "@/flag/flag"
import type * as SDK from "@opencode-ai/sdk/v2"

export namespace ShareNext {
  const log = Log.create({ service: "share-next" })

  /** 
   * 检查分享功能是否被禁用
   * - 离线模式下禁用
   * - 显式设置 OPENCODE_DISABLE_SHARE=true 时禁用
   * - 非企业版默认禁用（除非显式设置 OPENCODE_ENABLE_SHARE=true）
   */
  async function isDisabled() {
    if (Flag.OPENCODE_OFFLINE || Flag.OPENCODE_DISABLE_SHARE) {
      return true
    }
    // 检查是否为企业版（有 enterprise.url 配置）
    const config = await Config.get()
    const isEnterprise = !!config.enterprise?.url
    // 企业版默认启用分享，非企业版默认禁用（除非显式启用）
    if (isEnterprise) {
      return false
    }
    // 非企业版：默认禁用，除非显式设置 OPENCODE_ENABLE_SHARE=true
    return !Flag.OPENCODE_ENABLE_SHARE
  }

  async function url() {
    if (await isDisabled()) {
      return null
    }
    return Config.get().then((x) => x.enterprise?.url ?? "https://opncd.ai")
  }

  export async function init() {
    // 离线模式或禁用分享时，跳过所有分享相关的事件订阅
    if (await isDisabled()) {
      log.info("share disabled (offline mode, non-enterprise, or OPENCODE_DISABLE_SHARE=true)")
      return
    }

    Bus.subscribe(Session.Event.Updated, async (evt) => {
      await sync(evt.properties.info.id, [
        {
          type: "session",
          data: evt.properties.info,
        },
      ])
    })
    Bus.subscribe(MessageV2.Event.Updated, async (evt) => {
      await sync(evt.properties.info.sessionID, [
        {
          type: "message",
          data: evt.properties.info,
        },
      ])
      if (evt.properties.info.role === "user") {
        await sync(evt.properties.info.sessionID, [
          {
            type: "model",
            data: [
              await Provider.getModel(evt.properties.info.model.providerID, evt.properties.info.model.modelID).then(
                (m) => m,
              ),
            ],
          },
        ])
      }
    })
    Bus.subscribe(MessageV2.Event.PartUpdated, async (evt) => {
      await sync(evt.properties.part.sessionID, [
        {
          type: "part",
          data: evt.properties.part,
        },
      ])
    })
    Bus.subscribe(Session.Event.Diff, async (evt) => {
      await sync(evt.properties.sessionID, [
        {
          type: "session_diff",
          data: evt.properties.diff,
        },
      ])
    })
  }

  export async function create(sessionID: string) {
    // 离线模式或禁用分享时，直接返回错误
    if (await isDisabled()) {
      const config = await Config.get()
      const isEnterprise = !!config.enterprise?.url
      if (!isEnterprise) {
        throw new Error("Share is only available for enterprise users. Configure enterprise.url in your config or set OPENCODE_ENABLE_SHARE=true to enable.")
      }
      throw new Error("Share is disabled. Set OPENCODE_OFFLINE=false or OPENCODE_DISABLE_SHARE=false to enable.")
    }

    log.info("creating share", { sessionID })
    const baseUrl = await url()
    if (!baseUrl) {
      throw new Error("Share URL is not available")
    }
    const result = await fetch(`${baseUrl}/api/share`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ sessionID: sessionID }),
    })
      .then((x) => x.json())
      .then((x) => x as { id: string; url: string; secret: string })
    await Storage.write(["session_share", sessionID], result)
    fullSync(sessionID)
    return result
  }

  function get(sessionID: string) {
    return Storage.read<{
      id: string
      secret: string
      url: string
    }>(["session_share", sessionID])
  }

  type Data =
    | {
        type: "session"
        data: SDK.Session
      }
    | {
        type: "message"
        data: SDK.Message
      }
    | {
        type: "part"
        data: SDK.Part
      }
    | {
        type: "session_diff"
        data: SDK.FileDiff[]
      }
    | {
        type: "model"
        data: SDK.Model[]
      }

  const queue = new Map<string, { timeout: NodeJS.Timeout; data: Map<string, Data> }>()
  async function sync(sessionID: string, data: Data[]) {
    const existing = queue.get(sessionID)
    if (existing) {
      for (const item of data) {
        existing.data.set("id" in item ? (item.id as string) : ulid(), item)
      }
      return
    }

    const dataMap = new Map<string, Data>()
    for (const item of data) {
      dataMap.set("id" in item ? (item.id as string) : ulid(), item)
    }

    const timeout = setTimeout(async () => {
      const queued = queue.get(sessionID)
      if (!queued) return
      queue.delete(sessionID)
      const share = await get(sessionID).catch(() => undefined)
      if (!share) return

      await fetch(`${await url()}/api/share/${share.id}/sync`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          secret: share.secret,
          data: Array.from(queued.data.values()),
        }),
      })
    }, 1000)
    queue.set(sessionID, { timeout, data: dataMap })
  }

  export async function remove(sessionID: string) {
    log.info("removing share", { sessionID })
    const share = await get(sessionID)
    if (!share) return
    await fetch(`${await url()}/api/share/${share.id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        secret: share.secret,
      }),
    })
    await Storage.remove(["session_share", sessionID])
  }

  async function fullSync(sessionID: string) {
    log.info("full sync", { sessionID })
    const session = await Session.get(sessionID)
    const diffs = await Session.diff(sessionID)
    const messages = await Array.fromAsync(MessageV2.stream(sessionID))
    const models = await Promise.all(
      messages
        .filter((m) => m.info.role === "user")
        .map((m) => (m.info as SDK.UserMessage).model)
        .map((m) => Provider.getModel(m.providerID, m.modelID).then((m) => m)),
    )
    await sync(sessionID, [
      {
        type: "session",
        data: session,
      },
      ...messages.map((x) => ({
        type: "message" as const,
        data: x.info,
      })),
      ...messages.flatMap((x) => x.parts.map((y) => ({ type: "part" as const, data: y }))),
      {
        type: "session_diff",
        data: diffs,
      },
      {
        type: "model",
        data: models,
      },
    ])
  }
}
