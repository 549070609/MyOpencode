import type { Argv } from "yargs"
import { UI } from "../ui"
import * as prompts from "@clack/prompts"
import { Installation } from "../../installation"

export const UpgradeCommand = {
  command: "upgrade [target]",
  describe: "upgrade opencode to the latest or a specific version",
  builder: (yargs: Argv) => {
    return yargs
      .positional("target", {
        describe: "version to upgrade to, for ex '0.1.48' or 'v0.1.48'",
        type: "string",
      })
      .option("method", {
        alias: "m",
        describe: "installation method to use",
        type: "string",
        choices: ["curl", "npm", "pnpm", "bun", "brew"],
      })
  },
  handler: async (args: { target?: string; method?: string }) => {
    UI.empty()
    UI.println(UI.logo("  "))
    UI.empty()
    prompts.intro("升级")
    const detectedMethod = await Installation.method()
    const method = (args.method as Installation.Method) ?? detectedMethod
    if (method === "unknown") {
      prompts.log.error(`opencode 安装在 ${process.execPath}，可能由包管理器管理`)
      const install = await prompts.select({
        message: "仍然安装？",
        options: [
          { label: "是", value: true },
          { label: "否", value: false },
        ],
        initialValue: false,
      })
      if (!install) {
        prompts.outro("完成")
        return
      }
    }
    prompts.log.info("使用方式: " + method)
    const target = args.target ? args.target.replace(/^v/, "") : await Installation.latest()

    if (Installation.VERSION === target) {
      prompts.log.warn(`跳过升级: ${target} 已安装`)
      prompts.outro("完成")
      return
    }

    prompts.log.info(`从 ${Installation.VERSION} → ${target}`)
    const spinner = prompts.spinner()
    spinner.start("升级中...")
    const err = await Installation.upgrade(method, target).catch((err) => err)
    if (err) {
      spinner.stop("升级失败", 1)
      if (err instanceof Installation.UpgradeFailedError) prompts.log.error(err.data.stderr)
      else if (err instanceof Error) prompts.log.error(err.message)
      prompts.outro("完成")
      return
    }
    spinner.stop("升级完成")
    prompts.outro("完成")
  },
}
