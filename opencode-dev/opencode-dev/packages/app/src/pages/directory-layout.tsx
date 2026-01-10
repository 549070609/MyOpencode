import { createMemo, Show, Switch, Match, type ParentProps } from "solid-js"
import { useNavigate, useParams } from "@solidjs/router"
import { SDKProvider, useSDK } from "@/context/sdk"
import { SyncProvider, useSync } from "@/context/sync"
import { LocalProvider } from "@/context/local"

import { base64Decode } from "@opencode-ai/util/encode"
import { DataProvider } from "@opencode-ai/ui/context"
import { Logo } from "@opencode-ai/ui/logo"
import { Spinner } from "@opencode-ai/ui/spinner"
import { useI18n } from "@/i18n"

function ProjectLoadingScreen(props: { directory?: string }) {
  const { t } = useI18n()

  // Shorten the path for display (show last 2-3 parts)
  const shortPath = () => {
    if (!props.directory) return ""
    const parts = props.directory.replace(/\\/g, "/").split("/").filter(Boolean)
    if (parts.length <= 2) return props.directory
    return ".../" + parts.slice(-2).join("/")
  }

  return (
    <div class="h-full w-full flex flex-col items-center justify-center bg-background-base">
      <div class="relative">
        <Logo class="w-xl opacity-12" />
        <div class="absolute -bottom-4 left-1/2 -translate-x-1/2">
          <Spinner class="size-6 text-text-weak" />
        </div>
      </div>
      <div class="mt-10 flex flex-col items-center gap-2">
        <div class="text-14-regular text-text-weak">{t("common.loadingProject")}</div>
        <Show when={props.directory}>
          <div class="text-12-mono text-text-weakest max-w-80 truncate" title={props.directory}>
            {shortPath()}
          </div>
        </Show>
      </div>
    </div>
  )
}

function SyncContent(props: ParentProps & { directory: string }) {
  const sync = useSync()
  const sdk = useSDK()
  const navigate = useNavigate()
  const params = useParams()
  const { t } = useI18n()

  const respond = (input: {
    sessionID: string
    permissionID: string
    response: "once" | "always" | "reject"
  }) => sdk.client.permission.respond(input)

  const navigateToSession = (sessionID: string) => {
    navigate(`/${params.dir}/session/${sessionID}`)
  }

  return (
    <Switch fallback={<ProjectLoadingScreen directory={props.directory} />}>
      <Match when={sync.ready}>
        <DataProvider
          data={sync.data}
          directory={props.directory}
          onPermissionRespond={respond}
          onNavigateToSession={navigateToSession}
          translate={t}
        >
          <LocalProvider>{props.children}</LocalProvider>
        </DataProvider>
      </Match>
    </Switch>
  )
}

export default function Layout(props: ParentProps) {
  const params = useParams()
  const directory = createMemo(() => {
    return base64Decode(params.dir!)
  })
  return (
    <Show when={params.dir} keyed>
      <SDKProvider directory={directory()}>
        <SyncProvider>
          <SyncContent directory={directory()}>{props.children}</SyncContent>
        </SyncProvider>
      </SDKProvider>
    </Show>
  )
}
