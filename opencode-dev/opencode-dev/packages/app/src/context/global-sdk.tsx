import { createOpencodeClient, type Event } from "@opencode-ai/sdk/v2/client"
import { createSimpleContext } from "@opencode-ai/ui/context"
import { createGlobalEmitter } from "@solid-primitives/event-bus"
import { batch, onCleanup } from "solid-js"
import { usePlatform } from "./platform"
import { useServer } from "./server"

export const { use: useGlobalSDK, provider: GlobalSDKProvider } = createSimpleContext({
  name: "GlobalSDK",
  init: () => {
    const server = useServer()
    const platform = usePlatform()
    const abort = new AbortController()

    const url = server.url
    console.log("[GlobalSDK] Initializing...")
    console.log("[GlobalSDK] server.url:", url)
    console.log("[GlobalSDK] server.ready():", server.ready())
    console.log("[GlobalSDK] server.healthy():", server.healthy())

    if (!url) {
      console.error("[GlobalSDK] ERROR: No server URL available!")
    }

    // For localhost requests, use native fetch as tauriFetch has issues with localhost
    const isLocalhost = url?.includes("127.0.0.1") || url?.includes("localhost")
    const fetchFn = isLocalhost ? globalThis.fetch : platform.fetch
    console.log("[GlobalSDK] Using fetch:", isLocalhost ? "native (localhost)" : "platform")

    const eventSdk = createOpencodeClient({
      baseUrl: url,
      fetch: fetchFn,
      signal: abort.signal,
    })
    const emitter = createGlobalEmitter<{
      [key: string]: Event
    }>()

    type Queued = { directory: string; payload: Event }

    let queue: Array<Queued | undefined> = []
    const coalesced = new Map<string, number>()
    let timer: ReturnType<typeof setTimeout> | undefined
    let last = 0

    const key = (directory: string, payload: Event) => {
      if (payload.type === "session.status") return `session.status:${directory}:${payload.properties.sessionID}`
      if (payload.type === "lsp.updated") return `lsp.updated:${directory}`
      if (payload.type === "message.part.updated") {
        const part = payload.properties.part
        return `message.part.updated:${directory}:${part.messageID}:${part.id}`
      }
    }

    const flush = () => {
      if (timer) clearTimeout(timer)
      timer = undefined

      const events = queue
      queue = []
      coalesced.clear()
      if (events.length === 0) return

      last = Date.now()
      batch(() => {
        for (const event of events) {
          if (!event) continue
          emitter.emit(event.directory, event.payload)
        }
      })
    }

    const schedule = () => {
      if (timer) return
      const elapsed = Date.now() - last
      timer = setTimeout(flush, Math.max(0, 16 - elapsed))
    }

    const stop = () => {
      flush()
    }

    void (async () => {
      console.log("[GlobalSDK] Starting event stream connection...")
      try {
        const events = await eventSdk.global.event()
        console.log("[GlobalSDK] Event stream connected")
        let yielded = Date.now()
        for await (const event of events.stream) {
          const directory = event.directory ?? "global"
          const payload = event.payload
          const k = key(directory, payload)
          if (k) {
            const i = coalesced.get(k)
            if (i !== undefined) {
              queue[i] = undefined
            }
            coalesced.set(k, queue.length)
          }
          queue.push({ directory, payload })
          schedule()

          if (Date.now() - yielded < 8) continue
          yielded = Date.now()
          await new Promise<void>((resolve) => setTimeout(resolve, 0))
        }
      } catch (err) {
        // Ignore AbortError - this is expected when component unmounts
        if (err instanceof Error && err.name === "AbortError") {
          console.log("[GlobalSDK] Event stream aborted (cleanup)")
          return
        }
        console.warn("[GlobalSDK] Event stream error:", err)
      }
    })()
      .finally(stop)
      .catch((err) => {
        // Ignore AbortError - this is expected when component unmounts
        if (err instanceof Error && err.name === "AbortError") {
          return
        }
        console.warn("[GlobalSDK] Event stream connection failed:", err)
      })

    onCleanup(() => {
      abort.abort()
      stop()
    })

    const sdk = createOpencodeClient({
      baseUrl: server.url,
      fetch: fetchFn,
      throwOnError: true,
    })

    return { url: server.url, client: sdk, event: emitter }
  },
})
