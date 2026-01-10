import { createOpencodeClient } from "@opencode-ai/sdk/v2/client"
import { createSimpleContext } from "@opencode-ai/ui/context"
import { batch, createEffect, createMemo, createSignal, onCleanup } from "solid-js"
import { createStore } from "solid-js/store"
import { usePlatform } from "@/context/platform"
import { Persist, persisted } from "@/utils/persist"

type StoredProject = { worktree: string; expanded: boolean }

export function normalizeServerUrl(input: string) {
  const trimmed = input.trim()
  if (!trimmed) return
  const withProtocol = /^https?:\/\//.test(trimmed) ? trimmed : `http://${trimmed}`
  return withProtocol.replace(/\/+$/, "")
}

export function serverDisplayName(url: string) {
  if (!url) return ""
  return url
    .replace(/^https?:\/\//, "")
    .replace(/\/+$/, "")
    .split("/")[0]
}

function projectsKey(url: string) {
  if (!url) return ""
  const host = url.replace(/^https?:\/\//, "").split(":")[0]
  if (host === "localhost" || host === "127.0.0.1") return "local"
  return url
}

export const { use: useServer, provider: ServerProvider } = createSimpleContext({
  name: "Server",
  init: (props: { defaultUrl: string }) => {
    const platform = usePlatform()

    console.log("[ServerProvider] Initializing with defaultUrl:", props.defaultUrl)
    console.log("[ServerProvider] Platform:", platform.platform)

    const [store, setStore, _, ready] = persisted(
      Persist.global("server", ["server.v3"]),
      createStore({
        list: [] as string[],
        projects: {} as Record<string, StoredProject[]>,
      }),
    )

    const [active, setActiveRaw] = createSignal("")

    function setActive(input: string) {
      const url = normalizeServerUrl(input)
      if (!url) return
      console.log("[ServerProvider] setActive:", url)
      setActiveRaw(url)
    }

    function add(input: string) {
      const url = normalizeServerUrl(input)
      if (!url) return

      const fallback = normalizeServerUrl(props.defaultUrl)
      if (fallback && url === fallback) {
        console.log("[ServerProvider] add: Using default URL", url)
        setActiveRaw(url)
        return
      }

      batch(() => {
        if (!store.list.includes(url)) {
          setStore("list", store.list.length, url)
        }
        setActiveRaw(url)
      })
    }

    function remove(input: string) {
      const url = normalizeServerUrl(input)
      if (!url) return

      const list = store.list.filter((x) => x !== url)
      const next = active() === url ? (list[0] ?? normalizeServerUrl(props.defaultUrl) ?? "") : active()

      batch(() => {
        setStore("list", list)
        setActiveRaw(next)
      })
    }

    // Fallback timer to ensure we don't wait forever for persisted store
    const FALLBACK_TIMEOUT_MS = 3000
    let fallbackApplied = false

    // Effect to set initial active URL once persisted store is ready
    createEffect(() => {
      const isReady = ready()
      const currentActive = active()
      console.log("[ServerProvider] Effect - ready:", isReady, "active:", currentActive)

      if (!isReady) {
        console.log("[ServerProvider] Waiting for persisted store to be ready...")
        return
      }
      if (currentActive) {
        console.log("[ServerProvider] Already have active URL:", currentActive)
        return
      }
      const url = normalizeServerUrl(props.defaultUrl)
      if (!url) {
        console.warn("[ServerProvider] No default URL available!")
        return
      }
      console.log("[ServerProvider] Setting active URL from default:", url)
      setActiveRaw(url)
    })

    // Fallback: if persisted store takes too long, use default URL directly
    setTimeout(() => {
      if (active()) {
        console.log("[ServerProvider] Fallback timer: URL already set, skipping")
        return
      }
      console.warn("[ServerProvider] Fallback timer triggered after", FALLBACK_TIMEOUT_MS, "ms")
      fallbackApplied = true
      const url = normalizeServerUrl(props.defaultUrl)
      if (url) {
        console.log("[ServerProvider] Fallback: Setting active URL to:", url)
        setActiveRaw(url)
      }
    }, FALLBACK_TIMEOUT_MS)

    const isReady = createMemo(() => {
      // Ready if we have an active URL (either from persisted store or fallback)
      const hasActive = !!active()
      console.log("[ServerProvider] isReady check - ready():", ready(), "hasActive:", hasActive, "fallbackApplied:", fallbackApplied)
      return hasActive
    })

    const [healthy, setHealthy] = createSignal<boolean | undefined>(undefined)

    const check = (url: string) => {
      // For localhost requests, use native fetch as tauriFetch has issues with localhost
      const isLocalhost = url?.includes("127.0.0.1") || url?.includes("localhost")
      const fetchFn = isLocalhost ? globalThis.fetch : platform.fetch
      const sdk = createOpencodeClient({
        baseUrl: url,
        fetch: fetchFn,
        signal: AbortSignal.timeout(3000),
      })
      return sdk.global
        .health()
        .then((x) => x.data?.healthy === true)
        .catch(() => false)
    }

    createEffect(() => {
      const url = active()
      if (!url) return

      setHealthy(undefined)

      let alive = true
      let busy = false

      const run = () => {
        if (busy) return
        busy = true
        void check(url)
          .then((next) => {
            if (!alive) return
            setHealthy(next)
          })
          .finally(() => {
            busy = false
          })
      }

      run()
      const interval = setInterval(run, 10_000)

      onCleanup(() => {
        alive = false
        clearInterval(interval)
      })
    })

    const origin = createMemo(() => projectsKey(active()))
    const projectsList = createMemo(() => store.projects[origin()] ?? [])
    const isLocal = createMemo(() => origin() === "local")

    return {
      ready: isReady,
      healthy,
      isLocal,
      get url() {
        return active()
      },
      get name() {
        return serverDisplayName(active())
      },
      get list() {
        return store.list
      },
      setActive,
      add,
      remove,
      projects: {
        list: projectsList,
        open(directory: string) {
          const key = origin()
          if (!key) return
          const current = store.projects[key] ?? []
          if (current.find((x) => x.worktree === directory)) return
          setStore("projects", key, [{ worktree: directory, expanded: true }, ...current])
        },
        close(directory: string) {
          const key = origin()
          if (!key) return
          const current = store.projects[key] ?? []
          setStore(
            "projects",
            key,
            current.filter((x) => x.worktree !== directory),
          )
        },
        expand(directory: string) {
          const key = origin()
          if (!key) return
          const current = store.projects[key] ?? []
          const index = current.findIndex((x) => x.worktree === directory)
          if (index !== -1) setStore("projects", key, index, "expanded", true)
        },
        collapse(directory: string) {
          const key = origin()
          if (!key) return
          const current = store.projects[key] ?? []
          const index = current.findIndex((x) => x.worktree === directory)
          if (index !== -1) setStore("projects", key, index, "expanded", false)
        },
        move(directory: string, toIndex: number) {
          const key = origin()
          if (!key) return
          const current = store.projects[key] ?? []
          const fromIndex = current.findIndex((x) => x.worktree === directory)
          if (fromIndex === -1 || fromIndex === toIndex) return
          const result = [...current]
          const [item] = result.splice(fromIndex, 1)
          result.splice(toIndex, 0, item)
          setStore("projects", key, result)
        },
      },
    }
  },
})
