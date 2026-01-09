import type { SupportedLanguage, I18nTranslations } from "./types"
import { enTranslations } from "./locales/en"
import { zhCNTranslations } from "./locales/zh-CN"

let currentLanguage: SupportedLanguage = "en"

const translations: Record<SupportedLanguage, I18nTranslations> = {
  en: enTranslations,
  "zh-CN": zhCNTranslations,
}

export function setLanguage(language: SupportedLanguage): void {
  currentLanguage = language
}

export function getLanguage(): SupportedLanguage {
  return currentLanguage
}

export function t(key: string, replacements?: Record<string, string>): string {
  const keys = key.split(".")
  let value: any = translations[currentLanguage]

  for (const k of keys) {
    if (value && typeof value === "object") {
      value = value[k]
    } else {
      return key
    }
  }

  if (typeof value !== "string") {
    return key
  }

  if (replacements) {
    return Object.entries(replacements).reduce(
      (text, [placeholder, replacement]) => 
        text.replace(new RegExp(`\\{${placeholder}\\}`, "g"), replacement),
      value
    )
  }

  return value
}

export function getTranslations(): I18nTranslations {
  return translations[currentLanguage]
}

export type { SupportedLanguage, I18nTranslations }
