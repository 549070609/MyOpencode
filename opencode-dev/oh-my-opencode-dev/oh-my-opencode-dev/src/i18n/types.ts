export type SupportedLanguage = "en" | "zh-CN"

export interface I18nTranslations {
  agents: {
    sisyphus: {
      role: string
      description: string
      [key: string]: string
    }
    oracle: {
      description: string
      [key: string]: string
    }
    librarian: {
      description: string
      [key: string]: string
    }
    explore: {
      description: string
      [key: string]: string
    }
    frontendEngineer: {
      description: string
      [key: string]: string
    }
    documentWriter: {
      description: string
      [key: string]: string
    }
    multimodalLooker: {
      description: string
      [key: string]: string
    }
  }
  tools: {
    [toolName: string]: {
      description: string
      [key: string]: string
    }
  }
  cli: {
    [key: string]: string | { [key: string]: string }
  }
  hooks: {
    [key: string]: string
  }
  errors: {
    [key: string]: string
  }
  common: {
    [key: string]: string
  }
}
