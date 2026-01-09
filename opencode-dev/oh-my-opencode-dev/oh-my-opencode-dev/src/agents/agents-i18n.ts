import { getTranslations } from "../i18n"

export function getAgentDescription(agentName: keyof ReturnType<typeof getTranslations>["agents"]): string {
  const translations = getTranslations()
  return translations.agents[agentName]?.description || ""
}
