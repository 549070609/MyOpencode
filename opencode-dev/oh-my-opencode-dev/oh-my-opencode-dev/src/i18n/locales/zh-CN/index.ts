import { agentsZhCN } from "./agents"
import { toolsZhCN } from "./tools"
import { cliZhCN } from "./cli"
import { commonZhCN } from "./common"
import type { I18nTranslations } from "../../types"

export const zhCNTranslations: I18nTranslations = {
  agents: {
    sisyphus: agentsZhCN.sisyphus,
    oracle: agentsZhCN.oracle,
    librarian: agentsZhCN.librarian,
    explore: agentsZhCN.explore,
    frontendEngineer: agentsZhCN.frontendEngineer,
    documentWriter: agentsZhCN.documentWriter,
    multimodalLooker: agentsZhCN.multimodalLooker,
  },
  tools: toolsZhCN,
  cli: cliZhCN,
  hooks: {},
  errors: {},
  common: commonZhCN,
}
