import { createMemo, createSignal, onMount, Show } from "solid-js"
import { createStore } from "solid-js/store"
import { useSync } from "@tui/context/sync"
import { useSDK } from "@tui/context/sdk"
import { useDialog } from "@tui/ui/dialog"
import { useTheme } from "@tui/context/theme"
import { DialogSelect } from "@tui/ui/dialog-select"
import { DialogPrompt } from "@tui/ui/dialog-prompt"
import { useKeyboard } from "@opentui/solid"
import { TextAttributes, TextareaRenderable } from "@opentui/core"
import { useToast } from "@tui/ui/toast"
import { Keybind } from "@/util/keybind"
import { DialogConfirm } from "@tui/ui/dialog-confirm"

// 主入口：Provider 设置列表
export function DialogProviderSettings() {
  const sync = useSync()
  const dialog = useDialog()
  const { theme } = useTheme()

  const connectedProviders = createMemo(() => {
    return sync.data.provider.filter((p) => {
      // 过滤出有认证源的 provider
      return p.source === "env" || p.source === "api" || p.source === "config"
    })
  })

  const options = createMemo(() => {
    return connectedProviders().map((provider) => ({
      title: provider.name,
      value: provider.id,
      description:
        provider.source === "env"
          ? "(环境变量)"
          : provider.source === "api"
            ? "(API Key)"
            : provider.source === "config"
              ? "(配置文件)"
              : "",
      onSelect() {
        dialog.replace(() => <ProviderEditForm providerID={provider.id} providerName={provider.name} />)
      },
    }))
  })

  return (
    <DialogSelect
      title="Provider 设置"
      options={options()}
      keybind={[
        {
          keybind: Keybind.parse("a")[0],
          title: "添加自定义",
          onTrigger() {
            dialog.replace(() => <AddCustomProvider />)
          },
        },
        {
          keybind: Keybind.parse("d")[0],
          title: "删除认证",
          onTrigger(option) {
            dialog.replace(() => <DeleteProviderAuth providerID={option.value as string} />)
          },
        },
      ]}
    />
  )
}

// Provider 编辑表单
interface ProviderEditFormProps {
  providerID: string
  providerName: string
}

function ProviderEditForm(props: ProviderEditFormProps) {
  const dialog = useDialog()
  const sdk = useSDK()
  const sync = useSync()
  const { theme } = useTheme()
  const toast = useToast()

  const [store, setStore] = createStore({
    activeField: "apiKey" as "apiKey" | "baseURL" | "timeout",
    apiKey: "",
    baseURL: "",
    timeout: "300000",
    saving: false,
  })

  let apiKeyRef: TextareaRenderable
  let baseURLRef: TextareaRenderable
  let timeoutRef: TextareaRenderable

  const fields = ["apiKey", "baseURL", "timeout"] as const

  onMount(() => {
    dialog.setSize("medium")
    setTimeout(() => {
      apiKeyRef?.focus()
    }, 10)
  })

  useKeyboard((evt) => {
    if (evt.name === "tab") {
      const currentIndex = fields.indexOf(store.activeField)
      const nextIndex = evt.shift ? (currentIndex - 1 + fields.length) % fields.length : (currentIndex + 1) % fields.length
      setStore("activeField", fields[nextIndex])

      // Focus the corresponding textarea
      setTimeout(() => {
        if (fields[nextIndex] === "apiKey") apiKeyRef?.focus()
        else if (fields[nextIndex] === "baseURL") baseURLRef?.focus()
        else if (fields[nextIndex] === "timeout") timeoutRef?.focus()
      }, 10)
      evt.preventDefault()
    }
    if (evt.name === "return" && evt.ctrl) {
      handleSave()
      evt.preventDefault()
    }
  })

  async function handleSave() {
    if (store.saving) return
    setStore("saving", true)

    try {
      // 保存 API Key 到 auth
      if (store.apiKey) {
        await sdk.client.auth.set({
          providerID: props.providerID,
          auth: { type: "api", key: store.apiKey },
        })
      }

      // 保存其他选项到 config
      const options: Record<string, unknown> = {}

      if (store.baseURL.trim()) {
        options.baseURL = store.baseURL.trim()
      }

      if (store.timeout.trim()) {
        if (store.timeout.trim().toLowerCase() === "false") {
          options.timeout = false
        } else {
          const timeoutValue = parseInt(store.timeout.trim())
          if (!isNaN(timeoutValue) && timeoutValue > 0) {
            options.timeout = timeoutValue
          }
        }
      }

      // 只有当有配置选项时才更新 config
      if (Object.keys(options).length > 0) {
        const config = {
          provider: {
            [props.providerID]: {
              options,
            },
          },
        }
        await sdk.client.config.update(config)
      }

      await sdk.client.instance.dispose()
      await sync.bootstrap()

      toast.show({ message: "配置已保存", variant: "info" })
      dialog.clear()
    } catch (error) {
      toast.error(error as Error)
    } finally {
      setStore("saving", false)
    }
  }

  return (
    <box paddingLeft={2} paddingRight={2} gap={1} paddingBottom={1}>
      <box flexDirection="row" justifyContent="space-between">
        <text attributes={TextAttributes.BOLD} fg={theme.text}>
          编辑 {props.providerName}
        </text>
        <text fg={theme.textMuted}>esc</text>
      </box>

      <box paddingTop={1} gap={1}>
        {/* API Key */}
        <box gap={0}>
          <text fg={store.activeField === "apiKey" ? theme.primary : theme.textMuted}>API Key:</text>
          <textarea
            ref={(val: TextareaRenderable) => (apiKeyRef = val)}
            height={1}
            placeholder="输入 API Key (留空保持不变)"
            textColor={theme.text}
            focusedTextColor={theme.text}
            cursorColor={theme.primary}
            onFocus={() => setStore("activeField", "apiKey")}
            onChange={(text) => setStore("apiKey", text)}
          />
        </box>

        {/* Base URL */}
        <box gap={0}>
          <text fg={store.activeField === "baseURL" ? theme.primary : theme.textMuted}>Base URL:</text>
          <textarea
            ref={(val: TextareaRenderable) => (baseURLRef = val)}
            height={1}
            placeholder="自定义 API 端点 (留空使用默认)"
            textColor={theme.text}
            focusedTextColor={theme.text}
            cursorColor={theme.primary}
            onFocus={() => setStore("activeField", "baseURL")}
            onChange={(text) => setStore("baseURL", text)}
          />
        </box>

        {/* Timeout */}
        <box gap={0}>
          <text fg={store.activeField === "timeout" ? theme.primary : theme.textMuted}>Timeout (ms):</text>
          <textarea
            ref={(val: TextareaRenderable) => (timeoutRef = val)}
            height={1}
            initialValue="300000"
            placeholder="超时时间 (输入 false 禁用)"
            textColor={theme.text}
            focusedTextColor={theme.text}
            cursorColor={theme.primary}
            onFocus={() => setStore("activeField", "timeout")}
            onChange={(text) => setStore("timeout", text)}
          />
        </box>
      </box>

      <box paddingTop={1} gap={1} flexDirection="row">
        <text fg={theme.text}>
          Tab <span style={{ fg: theme.textMuted }}>切换字段</span>
        </text>
        <text fg={theme.text}>
          Ctrl+Enter{" "}
          <span style={{ fg: theme.textMuted }}>{store.saving ? "保存中..." : "保存"}</span>
        </text>
      </box>
    </box>
  )
}

// 添加自定义 Provider
function AddCustomProvider() {
  const dialog = useDialog()
  const { theme } = useTheme()

  return (
    <DialogPrompt
      title="添加自定义 Provider"
      placeholder="Provider ID (如: my-openai-proxy)"
      description={() => (
        <box gap={1}>
          <text fg={theme.textMuted}>输入自定义 Provider ID，然后配置连接参数。</text>
          <text fg={theme.textMuted}>
            常用 ID: openai, anthropic, google, azure, openai-compatible
          </text>
        </box>
      )}
      onConfirm={(providerID) => {
        if (providerID && providerID.trim()) {
          dialog.replace(() => <ProviderEditForm providerID={providerID.trim()} providerName={providerID.trim()} />)
        }
      }}
    />
  )
}

// 删除认证确认
function DeleteProviderAuth(props: { providerID: string }) {
  const dialog = useDialog()
  const sdk = useSDK()
  const sync = useSync()
  const toast = useToast()

  async function handleConfirm() {
    try {
      await sdk.client.auth.remove({ providerID: props.providerID })
      await sdk.client.instance.dispose()
      await sync.bootstrap()
      toast.show({ message: "认证已删除", variant: "info" })
    } catch (error) {
      toast.error(error as Error)
    }
  }

  return (
    <DialogConfirm
      title="删除认证"
      message={`确定要删除 ${props.providerID} 的认证信息吗？`}
      onConfirm={handleConfirm}
      onCancel={() => {
        dialog.clear()
      }}
    />
  )
}

