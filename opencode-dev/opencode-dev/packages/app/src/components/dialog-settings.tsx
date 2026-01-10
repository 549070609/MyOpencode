import { Component, For, createSignal, createMemo, Show } from "solid-js"
import { useDialog } from "@opencode-ai/ui/context/dialog"
import { Dialog } from "@opencode-ai/ui/dialog"
import { List } from "@opencode-ai/ui/list"
import { Icon } from "@opencode-ai/ui/icon"
import { Button } from "@opencode-ai/ui/button"
import { useI18n, LOCALES, type LocaleKey } from "@/i18n"
import { showToast } from "@opencode-ai/ui/toast"
import { tryUseLocal } from "@/context/local"
import { popularProviders } from "@/hooks/use-providers"
import { Tabs } from "@kobalte/core/tabs"
import { useTheme, type ColorScheme } from "@opencode-ai/ui/theme"
import { CustomProviderSettings } from "./custom-provider-settings"

type SettingsTab = "language" | "model" | "theme" | "providers"

export const DialogSettings: Component = () => {
  const dialog = useDialog()
  const { locale, setLocale, t, locales } = useI18n()
  const local = tryUseLocal()
  const [activeTab, setActiveTab] = createSignal<SettingsTab>("language")

  const localeList = Object.entries(locales).map(([key, value]) => ({
    id: key as LocaleKey,
    name: value.name,
    nativeName: value.nativeName,
  }))

  const handleLocaleSelect = (item: typeof localeList[0] | undefined) => {
    if (!item) return
    
    const previousLocale = locale()
    setLocale(item.id)
    
    if (previousLocale !== item.id) {
      showToast({
        title: t("settings.languageChanged"),
        description: item.nativeName,
      })
    }
  }

  return (
    <Dialog title={t("settings.settings")} class="w-[560px]">
      <Tabs value={activeTab()} onChange={(v) => setActiveTab(v as SettingsTab)} class="flex flex-col">
        <Tabs.List class="flex border-b border-border-weak-base mb-4">
          <Tabs.Trigger
            value="language"
            class="px-4 py-2 text-14-medium text-text-base border-b-2 border-transparent data-[selected]:border-text-interactive-base data-[selected]:text-text-strong transition-colors"
          >
            {t("settings.language")}
          </Tabs.Trigger>
          <Tabs.Trigger
            value="theme"
            class="px-4 py-2 text-14-medium text-text-base border-b-2 border-transparent data-[selected]:border-text-interactive-base data-[selected]:text-text-strong transition-colors"
          >
            {t("settings.theme")}
          </Tabs.Trigger>
          <Show when={local}>
            <Tabs.Trigger
              value="model"
              class="px-4 py-2 text-14-medium text-text-base border-b-2 border-transparent data-[selected]:border-text-interactive-base data-[selected]:text-text-strong transition-colors"
            >
              {t("settings.defaultModel")}
            </Tabs.Trigger>
          </Show>
          <Tabs.Trigger
            value="providers"
            class="px-4 py-2 text-14-medium text-text-base border-b-2 border-transparent data-[selected]:border-text-interactive-base data-[selected]:text-text-strong transition-colors"
          >
            {t("settings.customProviders")}
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="language" class="min-h-[300px]">
          <List
            items={() => localeList}
            key={(x) => x?.id}
            onSelect={handleLocaleSelect}
          >
            {(item) => (
              <div class="px-1.25 w-full flex items-center justify-between gap-x-3">
                <div class="flex items-center gap-3">
                  <div class="flex flex-col">
                    <span class="text-14-medium text-text-strong">{item.nativeName}</span>
                    <span class="text-12-regular text-text-weak">{item.name}</span>
                  </div>
                </div>
                {locale() === item.id && (
                  <Icon name="check" class="size-4 text-icon-success-base" />
                )}
              </div>
            )}
          </List>
        </Tabs.Content>

        <Tabs.Content value="theme" class="min-h-[300px]">
          <ThemeSettings />
        </Tabs.Content>

        <Show when={local}>
          <Tabs.Content value="model" class="min-h-[300px]">
            <DefaultModelSettings local={local!} />
          </Tabs.Content>
        </Show>

        <Tabs.Content value="providers" class="min-h-[300px]">
          <CustomProviderSettings />
        </Tabs.Content>
      </Tabs>
    </Dialog>
  )
}

const ThemeSettings: Component = () => {
  const theme = useTheme()
  const { t } = useI18n()

  const colorSchemeOptions: { id: ColorScheme; label: string }[] = [
    { id: "system", label: t("settings.system") },
    { id: "light", label: t("settings.light") },
    { id: "dark", label: t("settings.dark") },
  ]

  const themeList = createMemo(() =>
    Object.entries(theme.themes()).map(([id, themeData]) => ({
      id,
      name: themeData.name,
    }))
  )

  const handleColorSchemeSelect = (item: typeof colorSchemeOptions[0] | undefined) => {
    if (!item) return
    const previous = theme.colorScheme()
    theme.setColorScheme(item.id)
    if (previous !== item.id) {
      showToast({
        title: t("settings.colorSchemeChanged"),
        description: item.label,
      })
    }
  }

  const handleThemeSelect = (item: ReturnType<typeof themeList>[number] | undefined) => {
    if (!item) return
    const previous = theme.themeId()
    theme.setTheme(item.id)
    if (previous !== item.id) {
      showToast({
        title: t("settings.themeChanged"),
        description: item.name,
      })
    }
  }

  return (
    <div class="flex flex-col gap-4">
      {/* Color Scheme Section */}
      <div class="flex flex-col gap-2">
        <span class="text-12-medium text-text-weak px-1">{t("settings.colorScheme")}</span>
        <div class="flex gap-2">
          <For each={colorSchemeOptions}>
            {(option) => (
              <button
                class={`flex-1 px-4 py-2.5 rounded-lg text-14-medium transition-all border ${
                  theme.colorScheme() === option.id
                    ? "bg-surface-interactive-base border-border-interactive-base text-text-strong"
                    : "bg-surface-base border-border-weak-base text-text-base hover:bg-surface-base-hover hover:border-border-base"
                }`}
                onClick={() => handleColorSchemeSelect(option)}
              >
                <div class="flex items-center justify-center gap-2">
                  <Icon 
                    name={option.id === "system" ? "monitor" : option.id === "light" ? "sun" : "moon"} 
                    class="size-4" 
                  />
                  <span>{option.label}</span>
                </div>
              </button>
            )}
          </For>
        </div>
      </div>

      {/* Theme Selection */}
      <div class="flex flex-col gap-2">
        <span class="text-12-medium text-text-weak px-1">{t("settings.selectTheme")}</span>
        <List
          items={themeList}
          key={(x) => x?.id}
          onSelect={handleThemeSelect}
        >
          {(item) => (
            <div class="px-1.25 w-full flex items-center justify-between gap-x-3">
              <div class="flex items-center gap-3">
                <div class="size-6 rounded-md border border-border-weak-base overflow-hidden flex">
                  <div class="w-1/2 bg-[#1a1a2e]" />
                  <div class="w-1/2 bg-[#f5f5f7]" />
                </div>
                <span class="text-14-medium text-text-strong">{item.name}</span>
              </div>
              {theme.themeId() === item.id && (
                <Icon name="check" class="size-4 text-icon-success-base" />
              )}
            </div>
          )}
        </List>
      </div>
    </div>
  )
}

const DefaultModelSettings: Component<{ local: ReturnType<typeof tryUseLocal> & {} }> = (props) => {
  const local = props.local
  const { t } = useI18n()

  const models = createMemo(() =>
    local.model
      .list()
      .filter((m) => local.model.visible({ modelID: m.id, providerID: m.provider.id }))
  )

  const currentModel = createMemo(() => local.model.current())

  const handleModelSelect = (model: ReturnType<typeof models>[number] | undefined) => {
    if (!model) return
    local.model.set({ modelID: model.id, providerID: model.provider.id }, { recent: true })
    showToast({
      title: t("settings.defaultModelChanged"),
      description: `${model.provider.name} / ${model.name}`,
    })
  }

  return (
    <List
      search={{ placeholder: t("model.searchModels"), autofocus: false }}
      emptyMessage={t("model.noModelResults")}
      key={(x) => `${x.provider.id}:${x.id}`}
      items={models}
      current={currentModel()}
      filterKeys={["provider.name", "name", "id"]}
      sortBy={(a, b) => a.name.localeCompare(b.name)}
      groupBy={(x) => x.provider.name}
      sortGroupsBy={(a, b) => {
        if (a.category === "Recent" && b.category !== "Recent") return -1
        if (b.category === "Recent" && a.category !== "Recent") return 1
        const aProvider = a.items[0].provider.id
        const bProvider = b.items[0].provider.id
        if (popularProviders.includes(aProvider) && !popularProviders.includes(bProvider)) return -1
        if (!popularProviders.includes(aProvider) && popularProviders.includes(bProvider)) return 1
        return popularProviders.indexOf(aProvider) - popularProviders.indexOf(bProvider)
      }}
      onSelect={handleModelSelect}
    >
      {(model) => (
        <div class="w-full flex items-center justify-between gap-x-2 text-13-regular">
          <span class="truncate">{model.name}</span>
          <Show when={currentModel()?.id === model.id && currentModel()?.provider.id === model.provider.id}>
            <Icon name="check" class="size-4 text-icon-success-base shrink-0" />
          </Show>
        </div>
      )}
    </List>
  )
}

