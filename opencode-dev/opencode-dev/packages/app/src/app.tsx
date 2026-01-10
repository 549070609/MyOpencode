import "@/index.css"
import { ErrorBoundary, Show, lazy, type ParentProps } from "solid-js"
import { Router, Route, Navigate } from "@solidjs/router"
import { MetaProvider } from "@solidjs/meta"
import { Font } from "@opencode-ai/ui/font"
import { MarkedProvider } from "@opencode-ai/ui/context/marked"
import { DiffComponentProvider } from "@opencode-ai/ui/context/diff"
import { CodeComponentProvider } from "@opencode-ai/ui/context/code"
import { Diff } from "@opencode-ai/ui/diff"
import { Code } from "@opencode-ai/ui/code"
import { ThemeProvider } from "@opencode-ai/ui/theme"
import { GlobalSyncProvider } from "@/context/global-sync"
import { PermissionProvider } from "@/context/permission"
import { LayoutProvider } from "@/context/layout"
import { GlobalSDKProvider } from "@/context/global-sdk"
import { ServerProvider, useServer } from "@/context/server"
import { TerminalProvider } from "@/context/terminal"
import { PromptProvider } from "@/context/prompt"
import { FileProvider } from "@/context/file"
import { NotificationProvider } from "@/context/notification"
import { DialogProvider } from "@opencode-ai/ui/context/dialog"
import { CommandProvider } from "@/context/command"
import { Logo } from "@opencode-ai/ui/logo"
import Layout from "@/pages/layout"
import DirectoryLayout from "@/pages/directory-layout"
import { ErrorPage } from "./pages/error"
import { Suspense } from "solid-js"
import { I18nProvider, useI18n } from "@/i18n"

const Home = lazy(() => import("@/pages/home"))
const Session = lazy(() => import("@/pages/session"))
const Loading = () => {
  const { t } = useI18n()
  return (
    <div class="size-full flex flex-col items-center justify-center bg-background-base">
      <Logo class="w-xl opacity-12 animate-pulse" />
      <div class="mt-8 text-14-regular text-text-weak">{t("common.loading")}</div>
    </div>
  )
}

declare global {
  interface Window {
    __OPENCODE__?: { updaterEnabled?: boolean; port?: number; serverReady?: boolean }
  }
}

// Calculate default server URL - this is called lazily to handle async initialization
function getDefaultServerUrl(): string {
  console.log("[App] Calculating defaultServerUrl...")
  console.log("[App] window.__OPENCODE__:", window.__OPENCODE__)
  console.log("[App] location.hostname:", location.hostname)
  console.log("[App] location.origin:", window.location.origin)

  const param = new URLSearchParams(document.location.search).get("url")
  if (param) {
    console.log("[App] Using URL param:", param)
    return param
  }

  if (location.hostname.includes("opencode.ai")) {
    console.log("[App] Using opencode.ai default: http://localhost:4096")
    return "http://localhost:4096"
  }

  // Check for Tauri environment with port
  if (window.__OPENCODE__?.port) {
    const url = `http://127.0.0.1:${window.__OPENCODE__.port}`
    console.log("[App] Using __OPENCODE__.port:", url)
    return url
  }

  // Check if we're in a Tauri-like environment (not web)
  const isTauriEnv = window.location.origin.startsWith("tauri://") ||
                     window.location.origin.startsWith("https://tauri.localhost") ||
                     window.location.protocol === "tauri:"

  if (isTauriEnv) {
    // In Tauri but no port set yet - this shouldn't happen normally
    // Log a warning and use a placeholder that will trigger health check failure
    console.warn("[App] Tauri environment detected but no port set! window.__OPENCODE__:", window.__OPENCODE__)
    // Return empty to force waiting
    return ""
  }

  if (import.meta.env.DEV) {
    const url = `http://${import.meta.env.VITE_OPENCODE_SERVER_HOST ?? "localhost"}:${import.meta.env.VITE_OPENCODE_SERVER_PORT ?? "4096"}`
    console.log("[App] Using DEV env:", url)
    return url
  }

  // Fallback: try to use origin for web mode
  const origin = window.location.origin
  if (origin && origin !== "null") {
    console.log("[App] Using location.origin:", origin)
    return origin
  }

  // Final fallback
  console.log("[App] Using fallback: http://127.0.0.1:4096")
  return "http://127.0.0.1:4096"
}

// Dynamic getter that re-checks __OPENCODE__ each time
function getOrComputeDefaultServerUrl(): string {
  // Always try to get the port from __OPENCODE__ first (it might be set later)
  if (window.__OPENCODE__?.port) {
    const url = `http://127.0.0.1:${window.__OPENCODE__.port}`
    console.log("[App] getOrComputeDefaultServerUrl using __OPENCODE__.port:", url)
    return url
  }

  // Fall back to computed URL
  const url = getDefaultServerUrl()
  console.log("[App] getOrComputeDefaultServerUrl computed:", url)
  return url
}

export function AppBaseProviders(props: ParentProps) {
  return (
    <MetaProvider>
      <Font />
      <ThemeProvider>
        <I18nProvider>
          <ErrorBoundary fallback={(error) => <ErrorPage error={error} />}>
            <DialogProvider>
              <MarkedProvider>
                <DiffComponentProvider component={Diff}>
                  <CodeComponentProvider component={Code}>{props.children}</CodeComponentProvider>
                </DiffComponentProvider>
              </MarkedProvider>
            </DialogProvider>
          </ErrorBoundary>
        </I18nProvider>
      </ThemeProvider>
    </MetaProvider>
  )
}

function ServerKey(props: ParentProps) {
  const server = useServer()
  const { t } = useI18n()

  // Log state changes for debugging
  console.log("[ServerKey] Rendering - url:", server.url, "ready:", server.ready(), "healthy:", server.healthy())

  return (
    <Show
      when={server.url}
      keyed
      fallback={
        <div class="h-screen w-screen flex flex-col items-center justify-center bg-background-base text-text-weak">
          <Logo class="w-xl opacity-12 animate-pulse" />
          <div class="text-16-medium mb-4 mt-8">{t("server.waitingForServerUrl")}</div>
          <div class="text-12-regular opacity-60 space-y-1">
            <div>{t("server.url")}: {server.url || "none"}</div>
            <div>{t("server.ready")}: {String(server.ready())}</div>
            <div>{t("server.checkConsoleForDetails")}</div>
          </div>
        </div>
      }
    >
      {props.children}
    </Show>
  )
}

export function AppInterface() {
  // Compute URL lazily when component renders (after initialization_script runs)
  const serverUrl = getOrComputeDefaultServerUrl()
  console.log("[AppInterface] Rendering with serverUrl:", serverUrl)

  return (
    <ServerProvider defaultUrl={serverUrl}>
      <ServerKey>
        <GlobalSDKProvider>
          <GlobalSyncProvider>
            <Router
              root={(props) => (
                <PermissionProvider>
                  <LayoutProvider>
                    <NotificationProvider>
                      <CommandProvider>
                        <Layout>{props.children}</Layout>
                      </CommandProvider>
                    </NotificationProvider>
                  </LayoutProvider>
                </PermissionProvider>
              )}
            >
              <Route
                path="/"
                component={() => (
                  <Suspense fallback={<Loading />}>
                    <Home />
                  </Suspense>
                )}
              />
              <Route path="/:dir" component={DirectoryLayout}>
                <Route path="/" component={() => <Navigate href="session" />} />
                <Route
                  path="/session/:id?"
                  component={(p) => (
                    <Show when={p.params.id ?? "new"} keyed>
                      <TerminalProvider>
                        <FileProvider>
                          <PromptProvider>
                            <Suspense fallback={<Loading />}>
                              <Session />
                            </Suspense>
                          </PromptProvider>
                        </FileProvider>
                      </TerminalProvider>
                    </Show>
                  )}
                />
              </Route>
            </Router>
          </GlobalSyncProvider>
        </GlobalSDKProvider>
      </ServerKey>
    </ServerProvider>
  )
}
