import { getTranslations } from "../i18n"

export function getToolDescription(toolName: string): string {
  const translations = getTranslations()
  return translations.tools[toolName]?.description || ""
}
