import { Component, Show } from "solid-js"
import { useDialog } from "@opencode-ai/ui/context/dialog"
import { popularProviders, useProviders } from "@/hooks/use-providers"
import { Dialog } from "@opencode-ai/ui/dialog"
import { List } from "@opencode-ai/ui/list"
import { Tag } from "@opencode-ai/ui/tag"
import { ProviderIcon } from "@opencode-ai/ui/provider-icon"
import { IconName } from "@opencode-ai/ui/icons/provider"
import { DialogConnectProvider } from "./dialog-connect-provider"
import { useI18n } from "@/i18n"

type ProviderItem = { id: string; name: string }

export const DialogSelectProvider: Component = () => {
  const dialog = useDialog()
  const providers = useProviders()
  const { t } = useI18n()

  const getGroup = (x: ProviderItem) => {
    return popularProviders.includes(x.id) ? t("provider.popular") : t("provider.other")
  }

  return (
    <Dialog title={t("provider.connectProvider")}>
      <List<ProviderItem>
        search={{ placeholder: t("provider.searchProviders"), autofocus: true }}
        activeIcon="plus-small"
        key={(x) => x?.id}
        items={providers.all}
        filterKeys={["id", "name"]}
        groupBy={getGroup}
        sortBy={(a, b) => {
          if (popularProviders.includes(a.id) && popularProviders.includes(b.id))
            return popularProviders.indexOf(a.id) - popularProviders.indexOf(b.id)
          return a.name.localeCompare(b.name)
        }}
        sortGroupsBy={(a, b) => {
          if (a.category === t("provider.popular")) return -1
          if (b.category === t("provider.popular")) return 1
          return 0
        }}
        onSelect={(x) => {
          if (!x) return
          dialog.show(() => <DialogConnectProvider provider={x.id} />)
        }}
      >
        {(i) => (
          <div class="px-1.25 w-full flex items-center gap-x-3">
            <ProviderIcon data-slot="list-item-extra-icon" id={i.id as IconName} />
            <span>{i.name}</span>
            <Show when={i.id === "opencode"}>
              <Tag>{t("provider.recommended")}</Tag>
            </Show>
            <Show when={i.id === "anthropic"}>
              <div class="text-14-regular text-text-weak">{t("provider.connectWithClaudeOrApi")}</div>
            </Show>
          </div>
        )}
      </List>
    </Dialog>
  )
}
