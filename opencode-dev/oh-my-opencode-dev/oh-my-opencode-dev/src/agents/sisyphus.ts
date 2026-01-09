import type { AgentConfig } from "@opencode-ai/sdk"
import { isGptModel } from "./types"
import type { AvailableAgent, AvailableTool, AvailableSkill } from "./sisyphus-prompt-builder"
import {
  buildKeyTriggersSection,
  buildToolSelectionTable,
  buildExploreSection,
  buildLibrarianSection,
  buildDelegationTable,
  buildFrontendSection,
  buildOracleSection,
  buildHardBlocksSection,
  buildAntiPatternsSection,
  categorizeTools,
} from "./sisyphus-prompt-builder"
import { buildSisyphusPrompt, getSisyphusDescription } from "./sisyphus-i18n"

const DEFAULT_MODEL = "anthropic/claude-opus-4-5"

const sisyphusPrompts = buildSisyphusPrompt()
const SISYPHUS_ROLE_SECTION = sisyphusPrompts.role

const SISYPHUS_PHASE0_STEP1_3 = sisyphusPrompts.phase0Step1_3

const SISYPHUS_PHASE1 = sisyphusPrompts.phase1

const SISYPHUS_PARALLEL_EXECUTION = sisyphusPrompts.parallelExecution

const SISYPHUS_PHASE2B_PRE_IMPLEMENTATION = sisyphusPrompts.phase2bPreImplementation

const SISYPHUS_DELEGATION_PROMPT_STRUCTURE = sisyphusPrompts.delegationPromptStructure

const SISYPHUS_GITHUB_WORKFLOW = sisyphusPrompts.githubWorkflow

const SISYPHUS_CODE_CHANGES = sisyphusPrompts.codeChanges

const SISYPHUS_PHASE2C = sisyphusPrompts.phase2c

const SISYPHUS_PHASE3 = sisyphusPrompts.phase3

const SISYPHUS_TASK_MANAGEMENT = sisyphusPrompts.taskManagement

const SISYPHUS_TONE_AND_STYLE = sisyphusPrompts.toneAndStyle

const SISYPHUS_SOFT_GUIDELINES = sisyphusPrompts.softGuidelines

function buildDynamicSisyphusPrompt(
  availableAgents: AvailableAgent[],
  availableTools: AvailableTool[] = [],
  availableSkills: AvailableSkill[] = []
): string {
  const keyTriggers = buildKeyTriggersSection(availableAgents, availableSkills)
  const toolSelection = buildToolSelectionTable(availableAgents, availableTools, availableSkills)
  const exploreSection = buildExploreSection(availableAgents)
  const librarianSection = buildLibrarianSection(availableAgents)
  const frontendSection = buildFrontendSection(availableAgents)
  const delegationTable = buildDelegationTable(availableAgents)
  const oracleSection = buildOracleSection(availableAgents)
  const hardBlocks = buildHardBlocksSection(availableAgents)
  const antiPatterns = buildAntiPatternsSection(availableAgents)

  const sections = [
    SISYPHUS_ROLE_SECTION,
    "<Behavior_Instructions>",
    "",
    "## Phase 0 - Intent Gate (EVERY message)",
    "",
    keyTriggers,
    "",
    SISYPHUS_PHASE0_STEP1_3,
    "",
    "---",
    "",
    SISYPHUS_PHASE1,
    "",
    "---",
    "",
    "## Phase 2A - Exploration & Research",
    "",
    toolSelection,
    "",
    exploreSection,
    "",
    librarianSection,
    "",
    SISYPHUS_PARALLEL_EXECUTION,
    "",
    "---",
    "",
    SISYPHUS_PHASE2B_PRE_IMPLEMENTATION,
    "",
    frontendSection,
    "",
    delegationTable,
    "",
    SISYPHUS_DELEGATION_PROMPT_STRUCTURE,
    "",
    SISYPHUS_GITHUB_WORKFLOW,
    "",
    SISYPHUS_CODE_CHANGES,
    "",
    "---",
    "",
    SISYPHUS_PHASE2C,
    "",
    "---",
    "",
    SISYPHUS_PHASE3,
    "",
    "</Behavior_Instructions>",
    "",
    oracleSection,
    "",
    SISYPHUS_TASK_MANAGEMENT,
    "",
    SISYPHUS_TONE_AND_STYLE,
    "",
    "<Constraints>",
    hardBlocks,
    "",
    antiPatterns,
    "",
    SISYPHUS_SOFT_GUIDELINES,
  ]

  return sections.filter((s) => s !== "").join("\n")
}

export function createSisyphusAgent(
  model: string = DEFAULT_MODEL,
  availableAgents?: AvailableAgent[],
  availableToolNames?: string[],
  availableSkills?: AvailableSkill[]
): AgentConfig {
  const tools = availableToolNames ? categorizeTools(availableToolNames) : []
  const skills = availableSkills ?? []
  const prompt = availableAgents
    ? buildDynamicSisyphusPrompt(availableAgents, tools, skills)
    : buildDynamicSisyphusPrompt([], tools, skills)

  const base = {
    description: getSisyphusDescription(),
    mode: "primary" as const,
    model,
    maxTokens: 64000,
    prompt,
    color: "#00CED1",
  }

  if (isGptModel(model)) {
    return { ...base, reasoningEffort: "medium" }
  }

  return { ...base, thinking: { type: "enabled", budgetTokens: 32000 } }
}

export const sisyphusAgent = createSisyphusAgent()
