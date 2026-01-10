import { Component, createSignal, For, Show, createMemo } from "solid-js"
import { createStore, produce } from "solid-js/store"
import { useDialog } from "@opencode-ai/ui/context/dialog"
import { Dialog } from "@opencode-ai/ui/dialog"
import { List } from "@opencode-ai/ui/list"
import { TextField } from "@opencode-ai/ui/text-field"
import { Button } from "@opencode-ai/ui/button"
import { Icon } from "@opencode-ai/ui/icon"
import { Switch } from "@opencode-ai/ui/switch"
import { showToast } from "@opencode-ai/ui/toast"
import { Collapsible } from "@opencode-ai/ui/collapsible"
import { IconButton } from "@opencode-ai/ui/icon-button"
import { useGlobalSDK } from "@/context/global-sdk"
import { useGlobalSync } from "@/context/global-sync"
import { useI18n } from "@/i18n"

// 自定义服务商的数据结构
export interface CustomProviderData {
  id: string
  name: string
  baseURL: string
  modelId: string
  modelName: string
  contextLimit: number
  outputLimit: number
  toolCall: boolean
  attachment: boolean
  reasoning: boolean
  createdAt: number
}

// 表单数据结构
interface CustomProviderForm {
  providerId: string
  providerName: string
  baseURL: string
  apiKey: string
  modelId: string
  modelName: string
  contextLimit: string
  outputLimit: string
  toolCall: boolean
  attachment: boolean
  reasoning: boolean
}

// 自定义服务商列表设置组件
export const CustomProviderSettings: Component = () => {
  const dialog = useDialog()
  const globalSync = useGlobalSync()
  const { t } = useI18n()

  // 从配置中获取自定义服务商列表
  const customProviders = createMemo(() => {
    const providers = globalSync.data.provider?.all
    if (!providers) return []
    // 过滤出使用 openai-compatible 的自定义服务商
    return providers.filter((p) => {
      // 检查是否是用户添加的自定义服务商（有 custom 标记或使用 openai-compatible）
      const config = globalSync.data.config?.provider?.[p.id]
      return config?.npm === "@ai-sdk/openai-compatible"
    })
  })

  const handleAddNew = () => {
    dialog.show(() => <DialogAddCustomProvider onSuccess={() => dialog.close()} />)
  }

  const handleEdit = (providerId: string) => {
    dialog.show(() => <DialogEditCustomProvider providerId={providerId} onSuccess={() => dialog.close()} />)
  }

  const handleDelete = (providerId: string, providerName: string) => {
    dialog.show(() => (
      <DialogDeleteCustomProvider
        providerId={providerId}
        providerName={providerName}
        onSuccess={() => dialog.close()}
      />
    ))
  }

  return (
    <div class="flex flex-col gap-4">
      {/* 顶部添加按钮 */}
      <div class="flex items-center justify-between px-1">
        <span class="text-12-medium text-text-weak">{t("customProvider.customProviderList")}</span>
        <Button variant="ghost" size="small" icon="plus" onClick={handleAddNew}>
          {t("customProvider.addNew")}
        </Button>
      </div>

      {/* 服务商列表 */}
      <Show
        when={customProviders().length > 0}
        fallback={
          <div class="flex flex-col items-center justify-center py-12 gap-4">
            <Icon name="package" class="size-12 text-icon-weak-base" />
            <div class="text-center">
              <div class="text-14-medium text-text-base">{t("customProvider.noProviders")}</div>
              <div class="text-12-regular text-text-weak mt-1">{t("customProvider.noProvidersDesc")}</div>
            </div>
            <Button variant="primary" icon="plus" onClick={handleAddNew}>
              {t("customProvider.addFirstProvider")}
            </Button>
          </div>
        }
      >
        <div class="flex flex-col gap-2">
          <For each={customProviders()}>
            {(provider) => (
              <div class="flex items-center justify-between p-3 rounded-lg border border-border-weak-base hover:border-border-base transition-colors">
                <div class="flex items-center gap-3">
                  <div class="size-10 rounded-lg bg-surface-raised-base flex items-center justify-center">
                    <Icon name="package" class="size-5 text-icon-base" />
                  </div>
                  <div class="flex flex-col">
                    <span class="text-14-medium text-text-strong">{provider.name}</span>
                    <span class="text-12-regular text-text-weak">{provider.id}</span>
                  </div>
                </div>
                <div class="flex items-center gap-1">
                  <IconButton
                    icon="edit"
                    variant="ghost"
                    size="small"
                    title={t("common.edit")}
                    onClick={() => handleEdit(provider.id)}
                  />
                  <IconButton
                    icon="trash"
                    variant="ghost"
                    size="small"
                    title={t("common.delete")}
                    onClick={() => handleDelete(provider.id, provider.name)}
                  />
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  )
}

// 添加自定义服务商对话框
const DialogAddCustomProvider: Component<{ onSuccess?: () => void }> = (props) => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()
  const { t } = useI18n()

  const [store, setStore] = createStore<CustomProviderForm>({
    providerId: "",
    providerName: "",
    baseURL: "",
    apiKey: "",
    modelId: "",
    modelName: "",
    contextLimit: "128000",
    outputLimit: "8192",
    toolCall: true,
    attachment: false,
    reasoning: false,
  })

  const [errors, setErrors] = createStore<Partial<Record<keyof CustomProviderForm, string>>>({})
  const [saving, setSaving] = createSignal(false)
  const [showAdvanced, setShowAdvanced] = createSignal(false)

  function validate(): boolean {
    const newErrors: Partial<Record<keyof CustomProviderForm, string>> = {}

    if (!store.providerId.trim()) {
      newErrors.providerId = t("customProvider.providerIdRequired")
    } else if (!/^[a-z0-9-]+$/.test(store.providerId)) {
      newErrors.providerId = t("customProvider.providerIdInvalid")
    }

    if (!store.providerName.trim()) {
      newErrors.providerName = t("customProvider.providerNameRequired")
    }

    if (!store.baseURL.trim()) {
      newErrors.baseURL = t("customProvider.baseURLRequired")
    } else {
      try {
        new URL(store.baseURL)
      } catch {
        newErrors.baseURL = t("customProvider.baseURLInvalid")
      }
    }

    if (!store.apiKey.trim()) {
      newErrors.apiKey = t("customProvider.apiKeyRequired")
    }

    if (!store.modelId.trim()) {
      newErrors.modelId = t("customProvider.modelIdRequired")
    }

    if (!store.modelName.trim()) {
      newErrors.modelName = t("customProvider.modelNameRequired")
    }

    const contextLimit = parseInt(store.contextLimit)
    if (isNaN(contextLimit) || contextLimit <= 0) {
      newErrors.contextLimit = t("customProvider.contextLimitInvalid")
    }

    const outputLimit = parseInt(store.outputLimit)
    if (isNaN(outputLimit) || outputLimit <= 0) {
      newErrors.outputLimit = t("customProvider.outputLimitInvalid")
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault()

    if (!validate()) return

    setSaving(true)

    try {
      // 构建 provider 配置
      const providerConfig = {
        provider: {
          [store.providerId]: {
            npm: "@ai-sdk/openai-compatible",
            name: store.providerName,
            options: {
              baseURL: store.baseURL,
            },
            models: {
              [store.modelId]: {
                name: store.modelName,
                tool_call: store.toolCall,
                attachment: store.attachment,
                reasoning: store.reasoning,
                limit: {
                  context: parseInt(store.contextLimit),
                  output: parseInt(store.outputLimit),
                },
              },
            },
          },
        },
      }

      // 保存配置
      await globalSDK.client.config.update(providerConfig)

      // 保存 API Key
      await globalSDK.client.auth.set({
        providerID: store.providerId,
        auth: {
          type: "api",
          key: store.apiKey,
        },
      })

      // 刷新全局状态
      await globalSDK.client.global.dispose()

      showToast({
        variant: "success",
        icon: "circle-check",
        title: t("customProvider.success"),
        description: t("customProvider.successDesc", { name: store.providerName }),
      })

      props.onSuccess?.()
      dialog.close()
    } catch (error) {
      console.error("Failed to add custom provider:", error)
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: t("customProvider.error"),
        description: String(error),
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog
      title={
        <div class="flex items-center gap-2">
          <IconButton icon="arrow-left" variant="ghost" tabIndex={-1} onClick={() => dialog.close()} />
          <span>{t("customProvider.title")}</span>
        </div>
      }
      class="dialog-large"
    >
      <form onSubmit={handleSubmit} class="flex flex-col gap-5 px-2.5 pb-4">
        {/* 基本信息 */}
        <div class="flex flex-col gap-4">
          <div class="text-14-medium text-text-base">{t("customProvider.basicInfo")}</div>

          <TextField
            label={t("customProvider.providerId")}
            placeholder="my-openai-proxy"
            value={store.providerId}
            onChange={(v) => setStore("providerId", v.toLowerCase().replace(/[^a-z0-9-]/g, "-"))}
            validationState={errors.providerId ? "invalid" : undefined}
            error={errors.providerId}
            description={t("customProvider.providerIdDesc")}
          />

          <TextField
            label={t("customProvider.providerName")}
            placeholder={t("customProvider.providerNamePlaceholder")}
            value={store.providerName}
            onChange={(v) => setStore("providerName", v)}
            validationState={errors.providerName ? "invalid" : undefined}
            error={errors.providerName}
          />

          <TextField
            label={t("customProvider.baseURL")}
            placeholder="https://api.example.com/v1"
            value={store.baseURL}
            onChange={(v) => setStore("baseURL", v)}
            validationState={errors.baseURL ? "invalid" : undefined}
            error={errors.baseURL}
            description={t("customProvider.baseURLDesc")}
          />

          <TextField
            label={t("customProvider.apiKey")}
            placeholder="sk-..."
            type="password"
            value={store.apiKey}
            onChange={(v) => setStore("apiKey", v)}
            validationState={errors.apiKey ? "invalid" : undefined}
            error={errors.apiKey}
          />
        </div>

        {/* 模型配置 */}
        <div class="flex flex-col gap-4">
          <div class="text-14-medium text-text-base">{t("customProvider.modelConfig")}</div>

          <TextField
            label={t("customProvider.modelId")}
            placeholder="gpt-4o"
            value={store.modelId}
            onChange={(v) => setStore("modelId", v)}
            validationState={errors.modelId ? "invalid" : undefined}
            error={errors.modelId}
            description={t("customProvider.modelIdDesc")}
          />

          <TextField
            label={t("customProvider.modelName")}
            placeholder={t("customProvider.modelNamePlaceholder")}
            value={store.modelName}
            onChange={(v) => setStore("modelName", v)}
            validationState={errors.modelName ? "invalid" : undefined}
            error={errors.modelName}
          />
        </div>

        {/* 高级配置 */}
        <Collapsible
          open={showAdvanced()}
          onOpenChange={setShowAdvanced}
          trigger={
            <div class="flex items-center gap-2 text-14-medium text-text-weak cursor-pointer hover:text-text-base transition-colors">
              <Icon name={showAdvanced() ? "chevron-down" : "chevron-right"} class="size-4" />
              <span>{t("customProvider.advancedConfig")}</span>
            </div>
          }
        >
          <div class="flex flex-col gap-4 pt-3">
            <div class="grid grid-cols-2 gap-3">
              <TextField
                label={t("customProvider.contextLimit")}
                placeholder="128000"
                value={store.contextLimit}
                onChange={(v) => setStore("contextLimit", v.replace(/\D/g, ""))}
                validationState={errors.contextLimit ? "invalid" : undefined}
                error={errors.contextLimit}
              />

              <TextField
                label={t("customProvider.outputLimit")}
                placeholder="8192"
                value={store.outputLimit}
                onChange={(v) => setStore("outputLimit", v.replace(/\D/g, ""))}
                validationState={errors.outputLimit ? "invalid" : undefined}
                error={errors.outputLimit}
              />
            </div>

            <div class="flex flex-col gap-3">
              <div class="flex items-center justify-between">
                <div class="flex flex-col">
                  <span class="text-14-medium text-text-base">{t("customProvider.toolCall")}</span>
                  <span class="text-12-regular text-text-weak">{t("customProvider.toolCallDesc")}</span>
                </div>
                <Switch checked={store.toolCall} onChange={(checked) => setStore("toolCall", checked)} />
              </div>

              <div class="flex items-center justify-between">
                <div class="flex flex-col">
                  <span class="text-14-medium text-text-base">{t("customProvider.attachment")}</span>
                  <span class="text-12-regular text-text-weak">{t("customProvider.attachmentDesc")}</span>
                </div>
                <Switch checked={store.attachment} onChange={(checked) => setStore("attachment", checked)} />
              </div>

              <div class="flex items-center justify-between">
                <div class="flex flex-col">
                  <span class="text-14-medium text-text-base">{t("customProvider.reasoning")}</span>
                  <span class="text-12-regular text-text-weak">{t("customProvider.reasoningDesc")}</span>
                </div>
                <Switch checked={store.reasoning} onChange={(checked) => setStore("reasoning", checked)} />
              </div>
            </div>
          </div>
        </Collapsible>

        {/* 提交按钮 */}
        <div class="flex justify-end gap-3 pt-2">
          <Button type="button" variant="ghost" onClick={() => dialog.close()}>
            {t("common.cancel")}
          </Button>
          <Button type="submit" variant="primary" disabled={saving()}>
            <Show when={saving()} fallback={t("customProvider.addProvider")}>
              <Icon name="loader" class="size-4 animate-spin" />
              <span>{t("customProvider.adding")}</span>
            </Show>
          </Button>
        </div>
      </form>
    </Dialog>
  )
}

// 编辑自定义服务商对话框
const DialogEditCustomProvider: Component<{ providerId: string; onSuccess?: () => void }> = (props) => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()
  const globalSync = useGlobalSync()
  const { t } = useI18n()

  // 获取现有配置
  const existingConfig = createMemo(() => {
    const config = globalSync.data.config?.provider?.[props.providerId]
    const providers = globalSync.data.provider?.all || []
    const provider = providers.find((p) => p.id === props.providerId)
    return { config, provider }
  })

  const [store, setStore] = createStore({
    baseURL: existingConfig().config?.options?.baseURL as string || "",
    apiKey: "", // API Key 不回显，需要重新输入才更新
    timeout: String(existingConfig().config?.options?.timeout || "300000"),
  })

  const [saving, setSaving] = createSignal(false)

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault()
    setSaving(true)

    try {
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
            [props.providerId]: {
              options,
            },
          },
        }
        await globalSDK.client.config.update(config)
      }

      // 如果输入了新的 API Key，则更新
      if (store.apiKey.trim()) {
        await globalSDK.client.auth.set({
          providerID: props.providerId,
          auth: { type: "api", key: store.apiKey },
        })
      }

      await globalSDK.client.global.dispose()

      showToast({
        variant: "success",
        icon: "circle-check",
        title: t("customProvider.updateSuccess"),
        description: t("customProvider.updateSuccessDesc", { name: existingConfig().provider?.name || props.providerId }),
      })

      props.onSuccess?.()
      dialog.close()
    } catch (error) {
      console.error("Failed to update provider:", error)
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: t("customProvider.updateError"),
        description: String(error),
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog
      title={
        <div class="flex items-center gap-2">
          <IconButton icon="arrow-left" variant="ghost" tabIndex={-1} onClick={() => dialog.close()} />
          <span>{t("customProvider.editTitle", { name: existingConfig().provider?.name || props.providerId })}</span>
        </div>
      }
    >
      <form onSubmit={handleSubmit} class="flex flex-col gap-5 px-2.5 pb-4">
        <TextField
          label={t("customProvider.baseURL")}
          placeholder="https://api.example.com/v1"
          value={store.baseURL}
          onChange={(v) => setStore("baseURL", v)}
          description={t("customProvider.baseURLEditDesc")}
        />

        <TextField
          label={t("customProvider.apiKey")}
          placeholder={t("customProvider.apiKeyEditPlaceholder")}
          type="password"
          value={store.apiKey}
          onChange={(v) => setStore("apiKey", v)}
          description={t("customProvider.apiKeyEditDesc")}
        />

        <TextField
          label={t("customProvider.timeout")}
          placeholder="300000"
          value={store.timeout}
          onChange={(v) => setStore("timeout", v)}
          description={t("customProvider.timeoutDesc")}
        />

        <div class="flex justify-end gap-3 pt-2">
          <Button type="button" variant="ghost" onClick={() => dialog.close()}>
            {t("common.cancel")}
          </Button>
          <Button type="submit" variant="primary" disabled={saving()}>
            <Show when={saving()} fallback={t("common.save")}>
              <Icon name="loader" class="size-4 animate-spin" />
              <span>{t("common.saving")}</span>
            </Show>
          </Button>
        </div>
      </form>
    </Dialog>
  )
}

// 删除确认对话框
const DialogDeleteCustomProvider: Component<{
  providerId: string
  providerName: string
  onSuccess?: () => void
}> = (props) => {
  const dialog = useDialog()
  const globalSDK = useGlobalSDK()
  const { t } = useI18n()

  const [deleting, setDeleting] = createSignal(false)

  async function handleDelete() {
    setDeleting(true)

    try {
      // 删除认证信息
      await globalSDK.client.auth.remove({ providerID: props.providerId })

      // 注意：目前 API 可能不支持直接删除 provider 配置
      // 需要通过设置为 null 或空来"禁用"
      // await globalSDK.client.config.update({
      //   provider: {
      //     [props.providerId]: null,
      //   },
      // })

      await globalSDK.client.global.dispose()

      showToast({
        variant: "success",
        icon: "circle-check",
        title: t("customProvider.deleteSuccess"),
        description: t("customProvider.deleteSuccessDesc", { name: props.providerName }),
      })

      props.onSuccess?.()
      dialog.close()
    } catch (error) {
      console.error("Failed to delete provider:", error)
      showToast({
        variant: "error",
        icon: "circle-ban-sign",
        title: t("customProvider.deleteError"),
        description: String(error),
      })
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Dialog title={t("customProvider.deleteTitle")}>
      <div class="flex flex-col gap-4 px-2.5 pb-4">
        <div class="text-14-regular text-text-base">
          {t("customProvider.deleteConfirm", { name: props.providerName })}
        </div>

        <div class="flex justify-end gap-3">
          <Button variant="ghost" onClick={() => dialog.close()}>
            {t("common.cancel")}
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={deleting()}>
            <Show when={deleting()} fallback={t("common.delete")}>
              <Icon name="loader" class="size-4 animate-spin" />
              <span>{t("customProvider.deleting")}</span>
            </Show>
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

// 导出添加对话框供外部使用（如服务商选择列表）
export { DialogAddCustomProvider }

