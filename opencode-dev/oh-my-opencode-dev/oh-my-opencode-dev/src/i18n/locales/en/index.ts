import { agentsEn } from "./agents"
import { toolsEn } from "./tools"
import { cliEn } from "./cli"
import { commonEn } from "./common"
import type { I18nTranslations } from "../../types"

export const enTranslations: I18nTranslations = {
  agents: {
    sisyphus: agentsEn.sisyphus,
    oracle: agentsEn.oracle,
    librarian: agentsEn.librarian,
    explore: agentsEn.explore,
    frontendEngineer: agentsEn.frontendEngineer,
    documentWriter: agentsEn.documentWriter,
    multimodalLooker: agentsEn.multimodalLooker,
  },
  tools: toolsEn,
  cli: cliEn,
  hooks: {},
  errors: {},
  common: commonEn,
}
