import { Bus } from "../bus"
import { Config } from "../config/config"
import { Installation } from "../installation"
import { Session } from "../session"
import { MessageV2 } from "../session/message-v2"
import { Log } from "../util/log"
import { Flag } from "../flag/flag"

export namespace Share {
  const log = Log.create({ service: "share" })

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

  let queue: Promise<void> = Promise.resolve()
  const pending = new Map<string, any>()

  export async function sync(key: string, content: any) {
    // 离线模式或非企业版下跳过同步
    if (await isDisabled()) return

    const [root, ...splits] = key.split("/")
    if (root !== "session") return
    const [sub, sessionID] = splits
    if (sub === "share") return
    const share = await Session.getShare(sessionID).catch(() => {})
    if (!share) return
    const { secret } = share
    pending.set(key, content)
    queue = queue
      .then(async () => {
        const content = pending.get(key)
        if (content === undefined) return
        pending.delete(key)

        return fetch(`${URL}/share_sync`, {
          method: "POST",
          body: JSON.stringify({
            sessionID: sessionID,
            secret,
            key: key,
            content,
          }),
        })
      })
      .then((x) => {
        if (x) {
          log.info("synced", {
            key: key,
            status: x.status,
          })
        }
      })
  }

  export async function init() {
    // 离线模式或禁用分享时，跳过所有分享相关的事件订阅
    if (await isDisabled()) {
      log.info("share disabled (offline mode, non-enterprise, or OPENCODE_DISABLE_SHARE=true)")
      return
    }

    Bus.subscribe(Session.Event.Updated, async (evt) => {
      await sync("session/info/" + evt.properties.info.id, evt.properties.info)
    })
    Bus.subscribe(MessageV2.Event.Updated, async (evt) => {
      await sync("session/message/" + evt.properties.info.sessionID + "/" + evt.properties.info.id, evt.properties.info)
    })
    Bus.subscribe(MessageV2.Event.PartUpdated, async (evt) => {
      await sync(
        "session/part/" +
          evt.properties.part.sessionID +
          "/" +
          evt.properties.part.messageID +
          "/" +
          evt.properties.part.id,
        evt.properties.part,
      )
    })
  }

  export const URL =
    process.env["OPENCODE_API"] ??
    (Installation.isPreview() || Installation.isLocal() ? "https://api.dev.opencode.ai" : "https://api.opencode.ai")

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

    return fetch(`${URL}/share_create`, {
      method: "POST",
      body: JSON.stringify({ sessionID: sessionID }),
    })
      .then((x) => x.json())
      .then((x) => x as { url: string; secret: string })
  }

  export async function remove(sessionID: string, secret: string) {
    // 离线模式或禁用分享时，直接返回
    if (await isDisabled()) {
      log.info("share remove skipped (offline mode or non-enterprise)")
      return
    }

    return fetch(`${URL}/share_delete`, {
      method: "POST",
      body: JSON.stringify({ sessionID, secret }),
    }).then((x) => x.json())
  }
}
