import type { Message, Session, Part, FileDiff, SessionStatus, PermissionRequest } from "@opencode-ai/sdk/v2"
import { createSimpleContext } from "./helper"
import { PreloadMultiFileDiffResult } from "@pierre/diffs/ssr"

type Data = {
  session: Session[]
  session_status: {
    [sessionID: string]: SessionStatus
  }
  session_diff: {
    [sessionID: string]: FileDiff[]
  }
  session_diff_preload?: {
    [sessionID: string]: PreloadMultiFileDiffResult<any>[]
  }
  permission?: {
    [sessionID: string]: PermissionRequest[]
  }
  message: {
    [sessionID: string]: Message[]
  }
  part: {
    [messageID: string]: Part[]
  }
}

export type PermissionRespondFn = (input: {
  sessionID: string
  permissionID: string
  response: "once" | "always" | "reject"
}) => void

export type NavigateToSessionFn = (sessionID: string) => void

export type TranslateFn = (key: string, values?: Record<string, string | number>) => string

// Default translations for UI components
const defaultTranslations: Record<string, string> = {
  "permission.deny": "Deny",
  "permission.allowAlways": "Allow always",
  "permission.allowOnce": "Allow once",
  "permission.agent": "Agent",
  "tooltip.copied": "Copied",
  "tooltip.copyToClipboard": "Copy to clipboard",
  "tool.read": "Read",
  "tool.list": "List",
  "tool.write": "Write",
  "tool.edit": "Edit",
  "tool.glob": "Glob",
  "tool.grep": "Grep",
  "tool.bash": "Bash",
  "tool.fetch": "Fetch",
  "tool.todoRead": "Read TODOs",
  "tool.todoWrite": "Write TODO",
  "tool.webSearch": "Web Search",
  "tool.task": "Task",
  "tool.shell": "Shell",
  "status.delegatingWork": "Delegating work",
  "status.planningNextSteps": "Planning next steps",
  "status.gatheringContext": "Gathering context",
  "status.searchingCodebase": "Searching the codebase",
  "status.searchingWeb": "Searching the web",
  "status.makingEdits": "Making edits",
  "status.runningCommands": "Running commands",
  "status.thinking": "Thinking",
  "status.gatheringThoughts": "Gathering thoughts",
  "status.consideringNextSteps": "Considering next steps",
  "status.hideSteps": "Hide steps",
  "status.showSteps": "Show steps",
  "status.newMessage": "New message",
  "status.loading": "Loading",
  "status.noResults": "No results",
  "status.retrying": "retrying",
  "status.retryingIn": "in {seconds}s",
  "status.for": "for",
  "status.response": "Response",
  "status.error": "Error",
  "status.sessionChanges": "Session changes",
  "status.collapseAll": "Collapse all",
  "status.expandAll": "Expand all",
  "status.unified": "Unified",
  "status.split": "Split",
  "image.preview": "Image preview",
}

function defaultTranslate(key: string, values?: Record<string, string | number>): string {
  let result = defaultTranslations[key] ?? key
  if (values) {
    for (const [k, v] of Object.entries(values)) {
      result = result.replace(`{${k}}`, String(v))
    }
  }
  return result
}

export const { use: useData, provider: DataProvider } = createSimpleContext({
  name: "Data",
  init: (props: {
    data: Data
    directory: string
    onPermissionRespond?: PermissionRespondFn
    onNavigateToSession?: NavigateToSessionFn
    translate?: TranslateFn
  }) => {
    return {
      get store() {
        return props.data
      },
      get directory() {
        return props.directory
      },
      respondToPermission: props.onPermissionRespond,
      navigateToSession: props.onNavigateToSession,
      t: props.translate ?? defaultTranslate,
    }
  },
})
