import { createContext, useContext, createSignal, createMemo, type ParentProps, type Accessor } from "solid-js"
import { createStore } from "solid-js/store"

// Import locale files
import en from "./locales/en.json"
import zhCN from "./locales/zh-CN.json"

// Available locales
export const LOCALES = {
  en: { name: "English", nativeName: "English", data: en },
  "zh-CN": { name: "Chinese (Simplified)", nativeName: "简体中文", data: zhCN },
} as const

export type LocaleKey = keyof typeof LOCALES
export type TranslationData = typeof en

// Get nested value from object using dot notation
function getNestedValue(obj: any, path: string): string | undefined {
  const keys = path.split(".")
  let current = obj
  for (const key of keys) {
    if (current === undefined || current === null) return undefined
    current = current[key]
  }
  return typeof current === "string" ? current : undefined
}

// Replace placeholders like {name} with values
function interpolate(template: string, values?: Record<string, string | number>): string {
  if (!values) return template
  return template.replace(/\{(\w+)\}/g, (_, key) => {
    const value = values[key]
    return value !== undefined ? String(value) : `{${key}}`
  })
}

// Storage key for persisting locale
const LOCALE_STORAGE_KEY = "opencode.locale"

// Get initial locale from storage or browser
function getInitialLocale(): LocaleKey {
  // Try to get from localStorage
  if (typeof localStorage !== "undefined") {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
    if (stored && stored in LOCALES) {
      return stored as LocaleKey
    }
  }
  
  // Try to detect from browser
  if (typeof navigator !== "undefined") {
    const browserLang = navigator.language
    if (browserLang.startsWith("zh")) {
      return "zh-CN"
    }
  }
  
  return "en"
}

// I18n context type
type I18nContextValue = {
  locale: Accessor<LocaleKey>
  setLocale: (locale: LocaleKey) => void
  t: (key: string, values?: Record<string, string | number>) => string
  locales: typeof LOCALES
}

const I18nContext = createContext<I18nContextValue>()

export function I18nProvider(props: ParentProps) {
  const [locale, setLocaleSignal] = createSignal<LocaleKey>(getInitialLocale())
  
  const setLocale = (newLocale: LocaleKey) => {
    setLocaleSignal(newLocale)
    // Persist to localStorage
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(LOCALE_STORAGE_KEY, newLocale)
    }
  }
  
  const currentData = createMemo(() => LOCALES[locale()].data)
  
  const t = (key: string, values?: Record<string, string | number>): string => {
    const data = currentData()
    const translation = getNestedValue(data, key)
    
    if (translation === undefined) {
      // Fallback to English
      const fallback = getNestedValue(en, key)
      if (fallback !== undefined) {
        console.warn(`[i18n] Missing translation for "${key}" in ${locale()}, using English fallback`)
        return interpolate(fallback, values)
      }
      // Return key if not found
      console.warn(`[i18n] Missing translation for "${key}"`)
      return key
    }
    
    return interpolate(translation, values)
  }
  
  const value: I18nContextValue = {
    locale,
    setLocale,
    t,
    locales: LOCALES,
  }
  
  return (
    <I18nContext.Provider value={value}>
      {props.children}
    </I18nContext.Provider>
  )
}

export function useI18n() {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error("useI18n must be used within I18nProvider")
  }
  return context
}

// Convenience hook for just the translation function
export function useTranslation() {
  const { t } = useI18n()
  return t
}

// Export locale keys for type safety
export type { LocaleKey as Locale }

