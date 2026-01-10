import {
  type Message,
  type Agent,
  type Session,
  type Part,
  type Config,
  type Path,
  type Project,
  type FileDiff,
  type Todo,
  type SessionStatus,
  type ProviderListResponse,
  type ProviderAuthResponse,
  type Command,
  type McpStatus,
  type LspStatus,
  type VcsInfo,
  type PermissionRequest,
  createOpencodeClient,
} from "@opencode-ai/sdk/v2/client"
import { createStore, produce, reconcile } from "solid-js/store"
import { Binary } from "@opencode-ai/util/binary"
import { retry } from "@opencode-ai/util/retry"
import { useGlobalSDK } from "./global-sdk"
import { usePlatform } from "./platform"
import { ErrorPage, type InitError } from "../pages/error"
import { Logo } from "@opencode-ai/ui/logo"
import { batch, createContext, useContext, onCleanup, onMount, type ParentProps, Switch, Match } from "solid-js"
import { showToast } from "@opencode-ai/ui/toast"
import { getFilename } from "@opencode-ai/util/path"

type State = {
  status: "loading" | "partial" | "complete"
  agent: Agent[]
  command: Command[]
  project: string
  provider: ProviderListResponse
  config: Config
  path: Path
  session: Session[]
  session_status: {
    [sessionID: string]: SessionStatus
  }
  session_diff: {
    [sessionID: string]: FileDiff[]
  }
  todo: {
    [sessionID: string]: Todo[]
  }
  permission: {
    [sessionID: string]: PermissionRequest[]
  }
  mcp: {
    [name: string]: McpStatus
  }
  lsp: LspStatus[]
  vcs: VcsInfo | undefined
  limit: number
  message: {
    [sessionID: string]: Message[]
  }
  part: {
    [messageID: string]: Part[]
  }
}

function createGlobalSync() {
  const globalSDK = useGlobalSDK()
  const platform = usePlatform()
  const [globalStore, setGlobalStore] = createStore<{
    ready: boolean
    error?: InitError
    path: Path
    project: Project[]
    provider: ProviderListResponse
    provider_auth: ProviderAuthResponse
  }>({
    ready: false,
    path: { state: "", config: "", worktree: "", directory: "", home: "" },
    project: [],
    provider: { all: [], connected: [], default: {} },
    provider_auth: {},
  })

  const children: Record<string, ReturnType<typeof createStore<State>>> = {}
  function child(directory: string) {
    if (!directory) console.error("No directory provided")
    if (!children[directory]) {
      children[directory] = createStore<State>({
        project: "",
        provider: { all: [], connected: [], default: {} },
        config: {},
        path: { state: "", config: "", worktree: "", directory: "", home: "" },
        status: "loading" as const,
        agent: [],
        command: [],
        session: [],
        session_status: {},
        session_diff: {},
        todo: {},
        permission: {},
        mcp: {},
        lsp: [],
        vcs: undefined,
        limit: 5,
        message: {},
        part: {},
      })
      bootstrapInstance(directory)
    }
    return children[directory]
  }

  async function loadSessions(directory: string) {
    const [store, setStore] = child(directory)
    globalSDK.client.session
      .list({ directory })
      .then((x) => {
        const fourHoursAgo = Date.now() - 4 * 60 * 60 * 1000
        const nonArchived = (x.data ?? [])
          .filter((s) => !!s?.id)
          .filter((s) => !s.time?.archived)
          .slice()
          .sort((a, b) => a.id.localeCompare(b.id))
        // Include up to the limit, plus any updated in the last 4 hours
        const sessions = nonArchived.filter((s, i) => {
          if (i < store.limit) return true
          const updated = new Date(s.time?.updated ?? s.time?.created).getTime()
          return updated > fourHoursAgo
        })
        setStore("session", reconcile(sessions, { key: "id" }))
      })
      .catch((err) => {
        console.error("Failed to load sessions", err)
        const project = getFilename(directory)
        showToast({ title: `Failed to load sessions for ${project}`, description: err.message })
      })
  }

  async function bootstrapInstance(directory: string) {
    console.log("[bootstrapInstance] Starting for directory:", directory)
    console.log("[bootstrapInstance] platform.fetch:", platform.fetch ? "defined" : "undefined")
    console.log("[bootstrapInstance] platform.platform:", platform.platform)
    if (!directory) {
      console.warn("[bootstrapInstance] No directory provided, skipping")
      return
    }
    const [store, setStore] = child(directory)
    
    // For localhost requests, use native fetch as tauriFetch has issues with localhost
    const isLocalhost = globalSDK.url.includes("127.0.0.1") || globalSDK.url.includes("localhost")
    const fetchFn = isLocalhost ? globalThis.fetch : platform.fetch
    console.log("[bootstrapInstance] Using fetchFn:", isLocalhost ? "native (localhost)" : "platform")
    
    const sdk = createOpencodeClient({
      baseUrl: globalSDK.url,
      fetch: fetchFn,
      directory,
      throwOnError: true,
    })

    console.log("[bootstrapInstance] SDK created with baseUrl:", globalSDK.url)

    const INSTANCE_REQUEST_TIMEOUT = 10000 // 10 seconds per request

    function withTimeout<T>(promise: Promise<T>, ms: number, name: string): Promise<T> {
      return Promise.race([
        promise,
        new Promise<T>((_, reject) =>
          setTimeout(() => reject(new Error(`${name} timed out after ${ms}ms`)), ms),
        ),
      ])
    }

    const blockingRequests = {
      project: async () => {
        console.log("[bootstrapInstance] Fetching project.current()...")
        const x = await withTimeout(sdk.project.current(), INSTANCE_REQUEST_TIMEOUT, "project.current()")
        console.log("[bootstrapInstance] project.current() success:", x.data?.id)
        setStore("project", x.data!.id)
      },
      provider: async () => {
        console.log("[bootstrapInstance] Fetching provider.list()...")
        const x = await withTimeout(sdk.provider.list(), INSTANCE_REQUEST_TIMEOUT, "provider.list()")
        console.log("[bootstrapInstance] provider.list() success, providers:", x.data?.all?.length)
        const data = x.data!
        setStore("provider", {
          ...data,
          all: data.all.map((provider) => ({
            ...provider,
            models: Object.fromEntries(
              Object.entries(provider.models).filter(([, info]) => info.status !== "deprecated"),
            ),
          })),
        })
      },
      agent: async () => {
        console.log("[bootstrapInstance] Fetching app.agents()...")
        const x = await withTimeout(sdk.app.agents(), INSTANCE_REQUEST_TIMEOUT, "app.agents()")
        console.log("[bootstrapInstance] app.agents() success, agents:", x.data?.length)
        setStore("agent", x.data ?? [])
      },
      config: async () => {
        console.log("[bootstrapInstance] Fetching config.get()...")
        const x = await withTimeout(sdk.config.get(), INSTANCE_REQUEST_TIMEOUT, "config.get()")
        console.log("[bootstrapInstance] config.get() success")
        setStore("config", x.data!)
      },
    }

    console.log("[bootstrapInstance] Starting blocking requests...")
    await Promise.all(
      Object.entries(blockingRequests).map(([name, p]) =>
        retry(p).catch((e) => {
          console.error(`[bootstrapInstance] ${name} failed:`, e)
          setGlobalStore("error", e)
        }),
      ),
    )
      .then(() => {
        console.log("[bootstrapInstance] Blocking requests complete, status:", store.status)
        if (store.status !== "complete") setStore("status", "partial")
        console.log("[bootstrapInstance] Starting non-blocking requests...")
        // non-blocking
        Promise.all([
          sdk.path.get().then((x) => { console.log("[bootstrapInstance] path.get() done"); setStore("path", x.data!) }),
          sdk.command.list().then((x) => { console.log("[bootstrapInstance] command.list() done"); setStore("command", x.data ?? []) }),
          sdk.session.status().then((x) => { console.log("[bootstrapInstance] session.status() done"); setStore("session_status", x.data!) }),
          loadSessions(directory),
          sdk.mcp.status().then((x) => { console.log("[bootstrapInstance] mcp.status() done"); setStore("mcp", x.data!) }),
          sdk.lsp.status().then((x) => { console.log("[bootstrapInstance] lsp.status() done"); setStore("lsp", x.data!) }),
          sdk.vcs.get().then((x) => { console.log("[bootstrapInstance] vcs.get() done"); setStore("vcs", x.data) }),
          sdk.permission.list().then((x) => {
            const grouped: Record<string, PermissionRequest[]> = {}
            for (const perm of x.data ?? []) {
              if (!perm?.id || !perm.sessionID) continue
              const existing = grouped[perm.sessionID]
              if (existing) {
                existing.push(perm)
                continue
              }
              grouped[perm.sessionID] = [perm]
            }

            batch(() => {
              for (const sessionID of Object.keys(store.permission)) {
                if (grouped[sessionID]) continue
                setStore("permission", sessionID, [])
              }
              for (const [sessionID, permissions] of Object.entries(grouped)) {
                setStore(
                  "permission",
                  sessionID,
                  reconcile(
                    permissions
                      .filter((p) => !!p?.id)
                      .slice()
                      .sort((a, b) => a.id.localeCompare(b.id)),
                    { key: "id" },
                  ),
                )
              }
            })
          }),
        ]).then(() => {
          console.log("[bootstrapInstance] All non-blocking requests complete, setting status to complete")
          setStore("status", "complete")
        }).catch((e) => {
          console.error("[bootstrapInstance] Non-blocking requests failed:", e)
        })
      })
      .catch((e) => {
        console.error("[bootstrapInstance] Blocking requests failed:", e)
        setGlobalStore("error", e)
      })
  }

  const unsub = globalSDK.event.listen((e) => {
    const directory = e.name
    const event = e.details

    if (directory === "global") {
      switch (event?.type) {
        case "global.disposed": {
          bootstrap()
          break
        }
        case "project.updated": {
          const result = Binary.search(globalStore.project, event.properties.id, (s) => s.id)
          if (result.found) {
            setGlobalStore("project", result.index, reconcile(event.properties))
            return
          }
          setGlobalStore(
            "project",
            produce((draft) => {
              draft.splice(result.index, 0, event.properties)
            }),
          )
          break
        }
      }
      return
    }

    const [store, setStore] = child(directory)
    switch (event.type) {
      case "server.instance.disposed": {
        bootstrapInstance(directory)
        break
      }
      case "session.updated": {
        const result = Binary.search(store.session, event.properties.info.id, (s) => s.id)
        if (event.properties.info.time.archived) {
          if (result.found) {
            setStore(
              "session",
              produce((draft) => {
                draft.splice(result.index, 1)
              }),
            )
          }
          break
        }
        if (result.found) {
          setStore("session", result.index, reconcile(event.properties.info))
          break
        }
        setStore(
          "session",
          produce((draft) => {
            draft.splice(result.index, 0, event.properties.info)
          }),
        )
        break
      }
      case "session.diff":
        setStore("session_diff", event.properties.sessionID, reconcile(event.properties.diff, { key: "file" }))
        break
      case "todo.updated":
        setStore("todo", event.properties.sessionID, reconcile(event.properties.todos, { key: "id" }))
        break
      case "session.status": {
        setStore("session_status", event.properties.sessionID, reconcile(event.properties.status))
        break
      }
      case "message.updated": {
        const messages = store.message[event.properties.info.sessionID]
        if (!messages) {
          setStore("message", event.properties.info.sessionID, [event.properties.info])
          break
        }
        const result = Binary.search(messages, event.properties.info.id, (m) => m.id)
        if (result.found) {
          setStore("message", event.properties.info.sessionID, result.index, reconcile(event.properties.info))
          break
        }
        setStore(
          "message",
          event.properties.info.sessionID,
          produce((draft) => {
            draft.splice(result.index, 0, event.properties.info)
          }),
        )
        break
      }
      case "message.removed": {
        const messages = store.message[event.properties.sessionID]
        if (!messages) break
        const result = Binary.search(messages, event.properties.messageID, (m) => m.id)
        if (result.found) {
          setStore(
            "message",
            event.properties.sessionID,
            produce((draft) => {
              draft.splice(result.index, 1)
            }),
          )
        }
        break
      }
      case "message.part.updated": {
        const part = event.properties.part
        const parts = store.part[part.messageID]
        if (!parts) {
          setStore("part", part.messageID, [part])
          break
        }
        const result = Binary.search(parts, part.id, (p) => p.id)
        if (result.found) {
          setStore("part", part.messageID, result.index, reconcile(part))
          break
        }
        setStore(
          "part",
          part.messageID,
          produce((draft) => {
            draft.splice(result.index, 0, part)
          }),
        )
        break
      }
      case "message.part.removed": {
        const parts = store.part[event.properties.messageID]
        if (!parts) break
        const result = Binary.search(parts, event.properties.partID, (p) => p.id)
        if (result.found) {
          setStore(
            "part",
            event.properties.messageID,
            produce((draft) => {
              draft.splice(result.index, 1)
            }),
          )
        }
        break
      }
      case "vcs.branch.updated": {
        setStore("vcs", { branch: event.properties.branch })
        break
      }
      case "permission.asked": {
        const sessionID = event.properties.sessionID
        const permissions = store.permission[sessionID]
        if (!permissions) {
          setStore("permission", sessionID, [event.properties])
          break
        }

        const result = Binary.search(permissions, event.properties.id, (p) => p.id)
        if (result.found) {
          setStore("permission", sessionID, result.index, reconcile(event.properties))
          break
        }

        setStore(
          "permission",
          sessionID,
          produce((draft) => {
            draft.splice(result.index, 0, event.properties)
          }),
        )
        break
      }
      case "permission.replied": {
        const permissions = store.permission[event.properties.sessionID]
        if (!permissions) break
        const result = Binary.search(permissions, event.properties.requestID, (p) => p.id)
        if (!result.found) break
        setStore(
          "permission",
          event.properties.sessionID,
          produce((draft) => {
            draft.splice(result.index, 1)
          }),
        )
        break
      }
      case "lsp.updated": {
        const isLocalhost = globalSDK.url?.includes("127.0.0.1") || globalSDK.url?.includes("localhost")
        const fetchFn = isLocalhost ? globalThis.fetch : platform.fetch
        const sdk = createOpencodeClient({
          baseUrl: globalSDK.url,
          fetch: fetchFn,
          directory,
          throwOnError: true,
        })
        sdk.lsp.status().then((x) => setStore("lsp", x.data ?? []))
        break
      }
    }
  })
  onCleanup(unsub)

  async function bootstrap() {
    console.log("[bootstrap] Starting bootstrap, server URL:", globalSDK.url)
    console.log("[bootstrap] platform.fetch:", platform.fetch ? "defined" : "undefined")

    if (!globalSDK.url) {
      console.error("[bootstrap] No server URL available!")
      setGlobalStore("error", new Error("No server URL configured"))
      return
    }

    // For localhost requests, use native fetch as tauriFetch has issues with localhost
    // tauriFetch returns 502 for localhost requests in some cases
    const isLocalhost = globalSDK.url.includes("127.0.0.1") || globalSDK.url.includes("localhost")
    const fetchFn = isLocalhost ? globalThis.fetch : (platform.fetch ?? globalThis.fetch)
    console.log("[bootstrap] Using fetch:", isLocalhost ? "native (localhost)" : "platform")

    // Wait for server to be healthy with retry - reduced timeout for faster feedback
    const maxWait = 15000
    const interval = 500
    const start = Date.now()

    let health: { healthy?: boolean } | undefined
    let attempts = 0
    let lastError: unknown

    while (Date.now() - start < maxWait) {
      attempts++
      console.log(`[bootstrap] Health check attempt ${attempts}...`)
      try {
        // Add timeout to individual health check request
        const controller = new AbortController()
        const timeoutId = setTimeout(() => {
          console.log("[bootstrap] Health check request timeout, aborting...")
          controller.abort()
        }, 5000)

        console.log("[bootstrap] Sending health request to:", globalSDK.url)
        const response = await fetchFn(`${globalSDK.url}/global/health`, {
          signal: controller.signal,
        })
        clearTimeout(timeoutId)

        console.log("[bootstrap] Health fetch response status:", response.status)
        const data = await response.json()
        console.log("[bootstrap] Health response data:", data)
        health = data
        if (health?.healthy) {
          console.log("[bootstrap] Server is healthy!")
          break
        }
      } catch (e) {
        lastError = e
        console.log("[bootstrap] Health check error:", e)
      }

      await new Promise((r) => setTimeout(r, interval))
    }

    if (!health?.healthy) {
      console.log("[bootstrap] Server health check failed after", attempts, "attempts")
      const errorMsg = lastError
        ? `Server at ${globalSDK.url} returned error: ${lastError}`
        : `Could not connect to server at ${globalSDK.url} after ${attempts} attempts`
      setGlobalStore("error", new Error(errorMsg))
      return
    }

    console.log("[bootstrap] Starting data fetch...")

    // Helper to fetch with timeout using platform.fetch
    const fetchWithTimeout = async (endpoint: string, timeout = 10000) => {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)
      try {
        const response = await fetchFn(`${globalSDK.url}${endpoint}`, {
          signal: controller.signal,
        })
        clearTimeout(timeoutId)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        return await response.json()
      } catch (e) {
        clearTimeout(timeoutId)
        throw e
      }
    }

    // Use Promise.allSettled to continue even if some requests fail
    const results = await Promise.allSettled([
      (async () => {
        console.log("[bootstrap] Fetching path...")
        const data = await fetchWithTimeout("/path")
        console.log("[bootstrap] path.get() success")
        setGlobalStore("path", data)
        return "path"
      })(),
      (async () => {
        console.log("[bootstrap] Fetching projects...")
        const data = await fetchWithTimeout("/project")
        console.log("[bootstrap] project.list() success, count:", data?.length)
        const projects = (data ?? [])
          .filter((p: any) => !!p?.id)
          .filter((p: any) => !!p.worktree && !p.worktree.includes("opencode-test"))
          .slice()
          .sort((a: any, b: any) => a.id.localeCompare(b.id))
        setGlobalStore("project", projects)
        return "project"
      })(),
      (async () => {
        console.log("[bootstrap] Fetching providers...")
        const data = await fetchWithTimeout("/provider")
        console.log("[bootstrap] provider.list() success")
        setGlobalStore("provider", {
          ...data,
          all: (data.all ?? []).map((provider: any) => ({
            ...provider,
            models: Object.fromEntries(
              Object.entries(provider.models ?? {}).filter(([, info]: [string, any]) => info.status !== "deprecated"),
            ),
          })),
        })
        return "provider"
      })(),
      (async () => {
        console.log("[bootstrap] Fetching provider auth...")
        const data = await fetchWithTimeout("/provider/auth")
        console.log("[bootstrap] provider.auth() success")
        setGlobalStore("provider_auth", data ?? {})
        return "provider_auth"
      })(),
    ])

    // Log results
    const fulfilled = results.filter((r) => r.status === "fulfilled")
    const rejected = results.filter((r) => r.status === "rejected")
    console.log("[bootstrap] Results - fulfilled:", fulfilled.length, "rejected:", rejected.length)

    if (rejected.length > 0) {
      console.error("[bootstrap] Some requests failed:")
      rejected.forEach((r, i) => {
        if (r.status === "rejected") {
          console.error(`  [${i}]`, r.reason)
        }
      })
    }

    // If critical requests failed, show error
    // path.get() is critical
    if (results[0].status === "rejected") {
      console.error("[bootstrap] Critical request (path.get) failed")
      setGlobalStore("error", (results[0] as PromiseRejectedResult).reason)
      return
    }

    // Set ready even if some non-critical requests failed
    console.log("[bootstrap] Setting ready=true")
    setGlobalStore("ready", true)
  }

  onMount(() => {
    console.log("[GlobalSync] onMount - calling bootstrap()")
    bootstrap()

    // Fallback timeout - if bootstrap hasn't completed after 30 seconds, show error
    const fallbackTimeout = setTimeout(() => {
      if (!globalStore.ready && !globalStore.error) {
        console.error("[GlobalSync] Bootstrap timeout - forcing error state")
        setGlobalStore("error", new Error("Application initialization timed out. Please check your connection and restart."))
      }
    }, 30000)

    onCleanup(() => clearTimeout(fallbackTimeout))
  })

  return {
    data: globalStore,
    get ready() {
      return globalStore.ready
    },
    get error() {
      return globalStore.error
    },
    child,
    bootstrap,
    project: {
      loadSessions,
    },
  }
}

const GlobalSyncContext = createContext<ReturnType<typeof createGlobalSync>>()

export function GlobalSyncProvider(props: ParentProps) {
  const value = createGlobalSync()

  // Debug logging
  console.log("[GlobalSyncProvider] Rendering - ready:", value.ready, "error:", value.error)

  return (
    <Switch
      fallback={
        <div class="h-screen w-screen flex flex-col items-center justify-center bg-background-base">
          <Logo class="w-xl opacity-12 animate-pulse" />
          <div class="mt-8 text-14-regular text-text-weak">Loading...</div>
          <div class="mt-2 text-12-regular text-text-weakest">Connecting to server...</div>
          <div class="mt-4 text-10-regular text-text-weakest opacity-50">Check DevTools console for details</div>
        </div>
      }
    >
      <Match when={value.error}>
        <ErrorPage error={value.error} />
      </Match>
      <Match when={value.ready}>
        <GlobalSyncContext.Provider value={value}>{props.children}</GlobalSyncContext.Provider>
      </Match>
    </Switch>
  )
}

export function useGlobalSync() {
  const context = useContext(GlobalSyncContext)
  if (!context) throw new Error("useGlobalSync must be used within GlobalSyncProvider")
  return context
}

