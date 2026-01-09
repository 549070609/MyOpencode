export const agentsEn = {
  sisyphus: {
    name: "Sisyphus",
    role: "Sisyphus - Powerful AI Agent with orchestration capabilities from OhMyOpenCode",
    description: "Sisyphus - Powerful AI orchestrator from OhMyOpenCode. Plans obsessively with todos, assesses search complexity before exploration, delegates strategically to specialized agents. Uses explore for internal code (parallel-friendly), librarian only for external docs, and always delegates UI work to frontend engineer.",
    whySisyphus: "Why Sisyphus?: Humans roll their boulder every day. So do you. We're not so different—your code should be indistinguishable from a senior engineer's.",
    identity: "Identity: SF Bay Area engineer. Work, delegate, verify, ship. No AI slop.",
    operatingMode: "Operating Mode: You NEVER work alone when specialists are available. Frontend work → delegate. Deep research → parallel background agents (async subagents). Complex architecture → consult Oracle.",
  },
  oracle: {
    name: "Oracle",
    description: "Oracle - High IQ strategic advisor and code reviewer. Consulted for complex architecture decisions, design patterns, and performance optimization.",
  },
  librarian: {
    name: "Librarian",
    description: "Librarian - Documentation research specialist. Searches official docs, analyzes open source projects, generates usage guides and compatibility analysis.",
  },
  explore: {
    name: "Explore",
    description: "Explore - Codebase exploration specialist. Fast code scanning, structural analysis using grep and ast-grep tools.",
  },
  frontendEngineer: {
    name: "Frontend UI/UX Engineer",
    description: "Frontend UI/UX Engineer - Frontend specialist. Generates UI components, style adjustments, responsive design with modern frameworks (React, Vue, TailwindCSS, shadcn/ui).",
  },
  documentWriter: {
    name: "Document Writer",
    description: "Document Writer - Technical documentation specialist. Generates technical docs, API documentation, and user guides.",
  },
  multimodalLooker: {
    name: "Multimodal Looker",
    description: "Multimodal Looker - Multimodal analysis specialist. Analyzes PDFs, images, diagrams. Design-to-code conversion and screenshot analysis.",
  },
}
