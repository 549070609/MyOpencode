import solidPlugin from "vite-plugin-solid"
import tailwindcss from "@tailwindcss/vite"
import { fileURLToPath } from "url"

/**
 * @type {import("vite").PluginOption}
 */
export default [
  {
    name: "opencode-desktop:config",
    config() {
      return {
        resolve: {
          alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
          },
        },
        worker: {
          format: "es",
        },
        build: {
          // Don't inline fonts as base64 - emit them as separate files
          assetsInlineLimit: 0,
        },
        assetsInclude: ["**/*.woff2", "**/*.woff"],
      }
    },
  },
  tailwindcss(),
  solidPlugin(),
]
