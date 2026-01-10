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
import { useI18n } from "@/i18n"

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

    // Helper function for retrying SDK calls with exponential backoff
    async function withRetry<T>(
      fn: () => Promise<T>,
      name: string,
      maxRetries = 5,
      timeout = 15000
    ): Promise<T> {
      let lastError: unknown
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          console.log(`[bootstrapInstance] Fetching ${name} (attempt ${attempt}/${maxRetries})...`)
          const result = await Promise.race([
            fn(),
            new Promise<never>((_, reject) =>
              setTimeout(() => reject(new Error(`${name} timed out after ${timeout}ms`)), timeout)
            ),
          ])
          console.log(`[bootstrapInstance] ${name} success`)
          return result
        } catch (e) {
          lastError = e
          console.log(`[bootstrapInstance] ${name} failed (attempt ${attempt}/${maxRetries}):`, e)
          
          if (attempt < maxRetries) {
            const delay = Math.min(500 * Math.pow(2, attempt - 1), 5000)
            console.log(`[bootstrapInstance] Retrying ${name} after ${delay}ms...`)
            await new Promise((r) => setTimeout(r, delay))
          }
        }
      }
      throw lastError
    }

    console.log("[bootstrapInstance] Starting blocking requests (sequentially)...")
    
    // Execute blocking requests sequentially to avoid parallel request issues in Tauri webview
    let hasError = false
    
    // project.current
    try {
      const x = await withRetry(() => sdk.project.current(), "project.current()")
      setStore("project", x.data!.id)
    } catch (e) {
      console.error("[bootstrapInstance] project.current() failed:", e)
      hasError = true
    }
    
    // provider.list
    try {
      const x = await withRetry(() => sdk.provider.list(), "provider.list()")
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
    } catch (e) {
      console.error("[bootstrapInstance] provider.list() failed:", e)
      hasError = true
    }
    
    // app.agents
    try {
      const x = await withRetry(() => sdk.app.agents(), "app.agents()")
      setStore("agent", x.data ?? [])
    } catch (e) {
      console.error("[bootstrapInstance] app.agents() failed:", e)
      hasError = true
    }
    
    // config.get
    try {
      const x = await withRetry(() => sdk.config.get(), "config.get()")
      setStore("config", x.data!)
    } catch (e) {
      console.error("[bootstrapInstance] config.get() failed:", e)
      hasError = true
    }

    console.log("[bootstrapInstance] Blocking requests complete, hasError:", hasError, "status:", store.status)
    if (store.status !== "complete") setStore("status", "partial")
    
    console.log("[bootstrapInstance] Starting non-blocking requests (sequentially)...")
    
    // Execute non-blocking requests sequentially too
    const nonBlockingTasks = [
      async () => {
        const x = await sdk.path.get()
        console.log("[bootstrapInstance] path.get() done")
        setStore("path", x.data!)
      },
      async () => {
        const x = await sdk.command.list()
        console.log("[bootstrapInstance] command.list() done")
        setStore("command", x.data ?? [])
      },
      async () => {
        const x = await sdk.session.status()
        console.log("[bootstrapInstance] session.status() done")
        setStore("session_status", x.data!)
      },
      async () => {
        await loadSessions(directory)
        console.log("[bootstrapInstance] loadSessions() done")
      },
      async () => {
        const x = await sdk.mcp.status()
        console.log("[bootstrapInstance] mcp.status() done")
        setStore("mcp", x.data!)
      },
      async () => {
        const x = await sdk.lsp.status()
        console.log("[bootstrapInstance] lsp.status() done")
        setStore("lsp", x.data!)
      },
      async () => {
        const x = await sdk.vcs.get()
        console.log("[bootstrapInstance] vcs.get() done")
        setStore("vcs", x.data)
      },
      async () => {
        const x = await sdk.permission.list()
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
        console.log("[bootstrapInstance] permission.list() done")
      },
    ]

    for (const task of nonBlockingTasks) {
      try {
        await task()
      } catch (e) {
        console.error("[bootstrapInstance] Non-blocking task failed:", e)
      }
    }
    
    console.log("[bootstrapInstance] All requests complete, setting status to complete")
    setStore("status", "complete")
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

    // Small delay to let other initialization tasks complete (Storage, etc.)
    await new Promise((r) => setTimeout(r, 100))

    // Helper to fetch with timeout and retry for all errors
    const fetchWithRetry = async (endpoint: string, maxRetries = 5, timeout = 15000) => {
      let lastError: unknown
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        const controller = new AbortController()
        const timeoutId = setTimeout(() => {
          console.log(`[bootstrap] Request to ${endpoint} timeout after ${timeout}ms, aborting...`)
          controller.abort()
        }, timeout)
        try {
          console.log(`[bootstrap] Fetching ${endpoint} (attempt ${attempt}/${maxRetries})...`)
          const response = await fetchFn(`${globalSDK.url}${endpoint}`, {
            signal: controller.signal,
          })
          clearTimeout(timeoutId)
          if (!response.ok) throw new Error(`HTTP ${response.status}`)
          const data = await response.json()
          console.log(`[bootstrap] ${endpoint} success`)
          return data
        } catch (e) {
          clearTimeout(timeoutId)
          lastError = e
          console.log(`[bootstrap] Fetch ${endpoint} failed (attempt ${attempt}/${maxRetries}):`, e)
          
          // Retry all errors with exponential backoff
          if (attempt < maxRetries) {
            const delay = Math.min(500 * Math.pow(2, attempt - 1), 5000) // 500ms, 1s, 2s, 4s, 5s
            console.log(`[bootstrap] Retrying ${endpoint} after ${delay}ms...`)
            await new Promise((r) => setTimeout(r, delay))
            continue
          }
        }
      }
      throw lastError
    }

    // Fetch sequentially to avoid potential issues with parallel requests in Tauri webview on Windows
    // This is more reliable than parallel requests which can cause AbortError in some environments
    const fetchSequentially = async () => {
      const errors: Array<{ name: string; error: unknown }> = []
      
      // Critical: path - use longer timeout and more retries for first request
      try {
        console.log("[bootstrap] Fetching path...")
        const data = await fetchWithRetry("/path", 5, 20000) // 5 retries, 20s timeout
        console.log("[bootstrap] path.get() success")
        setGlobalStore("path", data)
      } catch (e) {
        console.error("[bootstrap] path.get() failed:", e)
        errors.push({ name: "path", error: e })
      }
      
      // Non-critical: project
      try {
        console.log("[bootstrap] Fetching projects...")
        const data = await fetchWithRetry("/project")
        console.log("[bootstrap] project.list() success, count:", data?.length)
        const projects = (data ?? [])
          .filter((p: any) => !!p?.id)
          .filter((p: any) => !!p.worktree && !p.worktree.includes("opencode-test"))
          .slice()
          .sort((a: any, b: any) => a.id.localeCompare(b.id))
        setGlobalStore("project", projects)
      } catch (e) {
        console.error("[bootstrap] project.list() failed:", e)
        errors.push({ name: "project", error: e })
      }
      
      // Non-critical: provider
      try {
        console.log("[bootstrap] Fetching providers...")
        const data = await fetchWithRetry("/provider")
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
      } catch (e) {
        console.error("[bootstrap] provider.list() failed:", e)
        errors.push({ name: "provider", error: e })
      }
      
      // Non-critical: provider auth
      try {
        console.log("[bootstrap] Fetching provider auth...")
        const data = await fetchWithRetry("/provider/auth")
        console.log("[bootstrap] provider.auth() success")
        setGlobalStore("provider_auth", data ?? {})
      } catch (e) {
        console.error("[bootstrap] provider.auth() failed:", e)
        errors.push({ name: "provider_auth", error: e })
      }
      
      return errors
    }

    const errors = await fetchSequentially()
    
    // Map errors to results format for compatibility
    const results = [
      errors.find((e) => e.name === "path") ? { status: "rejected" as const, reason: errors.find((e) => e.name === "path")!.error } : { status: "fulfilled" as const, value: "path" },
      errors.find((e) => e.name === "project") ? { status: "rejected" as const, reason: errors.find((e) => e.name === "project")!.error } : { status: "fulfilled" as const, value: "project" },
      errors.find((e) => e.name === "provider") ? { status: "rejected" as const, reason: errors.find((e) => e.name === "provider")!.error } : { status: "fulfilled" as const, value: "provider" },
      errors.find((e) => e.name === "provider_auth") ? { status: "rejected" as const, reason: errors.find((e) => e.name === "provider_auth")!.error } : { status: "fulfilled" as const, value: "provider_auth" },
    ]

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
  const { t } = useI18n()

  // Debug logging
  console.log("[GlobalSyncProvider] Rendering - ready:", value.ready, "error:", value.error)

  return (
    <Switch
      fallback={
        <div class="h-screen w-screen flex flex-col items-center justify-center bg-background-base">
          <Logo class="w-xl opacity-12 animate-pulse" />
          <div class="mt-8 text-14-regular text-text-weak">{t("common.loading")}</div>
          <div class="mt-2 text-12-regular text-text-weakest">{t("common.connectingToServer")}</div>
          <div class="mt-4 text-10-regular text-text-weakest opacity-50">{t("common.checkDevTools")}</div>
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

