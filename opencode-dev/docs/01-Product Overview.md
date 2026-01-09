# OpenCode Product Overview

---

## 🎯 Product Positioning

**OpenCode** is the world's first truly open, provider-agnostic AI coding agent designed for developers who demand complete control, unmatched flexibility, and uncompromising performance.

> *"I aim to spark a software revolution by creating a world where agent-generated code is indistinguishable from human code, yet capable of achieving vastly more."*

As the only 100% open-source alternative to proprietary AI coding assistants, OpenCode breaks free from vendor lock-in while delivering enterprise-grade capabilities through a modern terminal-first architecture.

---

## 💎 Value Proposition

### For Individual Developers

- **Freedom from Vendor Lock-in**: Choose any AI provider—Claude, OpenAI, Google, or local models—without switching tools
- **Complete Transparency**: Every line of code is auditable, modifiable, and under your control
- **Unmatched Performance**: Zero screen flicker, instant response times, and intelligent resource management
- **Cost Optimization**: Pay only for what you use with competitive OpenCode Zen pricing or bring your own keys

### For Teams & Enterprises

- **Unified AI Development Platform**: Single interface for multiple AI models, providers, and workflows
- **Self-Hosting Capabilities**: Deploy on-premises for regulatory compliance and data security
- **Extensible Plugin Ecosystem**: Build custom tools, agents, and integrations tailored to your workflows
- **Multi-Model Orchestration**: Optimize costs and accuracy by selecting the right model for each task

---

## 🚀 Core Selling Points

### 1. 100% Open Source & Transparent
- **MIT License**: No hidden code, no telemetry, no surprises
- **Community-Driven**: 39K+ GitHub stars and rapidly growing
- **Self-Hostable**: Full control over data, models, and deployment
- **Auditable**: Every feature, tool, and integration is transparent

### 2. Provider-Agnostic Multi-Model Support
- **75+ AI Providers**: Anthropic, OpenAI, Google, Azure, AWS, Mistral, Grok, xAI, and more
- **OpenCode Zen**: Curated, tested models with competitive pricing
- **Bring Your Own Keys**: Use your existing subscriptions without middleman markups
- **Model Switching**: Seamlessly switch between providers per task or project

### 3. Complete LSP Integration
- **25+ Language Servers**: TypeScript, Python, Go, Rust, Java, C#, PHP, Ruby, and more
- **Real-Time Diagnostics**: Instant feedback on code quality and errors
- **Deep Code Intelligence**: Hover info, goto definition, find references, rename operations
- **Auto-Discovery**: LSP servers download automatically based on file extensions

### 4. Advanced Agent System
- **10+ Specialized Agents**: Sisyphus (orchestrator), Oracle (architecture), Librarian (research), Explore (pattern matching), Frontend UI/UX Engineer, Document Writer, Multimodal Looker, and more
- **Multi-Agent Orchestration**: Parallel execution, background tasks, and todo-driven workflows
- **Plan & Build Modes**: Risk-free exploration with read-only planning, then execute with confidence
- **Aggressive Parallelism**: Complete complex tasks faster through concurrent agent operations

### 5. Superior Terminal Experience
- **Zero Screen Flicker**: OpenTUI framework ensures smooth rendering
- **Keyboard-First Design**: Optimized for developers who live in terminal
- **Split-View Interface**: Code, files, and terminal in one screen
- **Mouse Support**: When you need it, modern interactions work seamlessly

### 6. Client/Server Architecture
- **Remote Control**: Run OpenCode on powerful servers, control from anywhere
- **Multiple Clients**: TUI, Desktop (Tauri), Web UI—all share the same backend
- **Future-Proof**: Mobile app and new client interfaces without backend changes
- **Scalable**: Deploy on-premises, in the cloud, or locally

---

## 🆚 Competitive Differentiation

### vs. Claude Code

| Feature | OpenCode | Claude Code |
|---------|----------|-------------|
| **Open Source** | ✅ 100% MIT License | ❌ Proprietary |
| **Model Support** | ✅ 75+ providers | ❌ Anthropic only |
| **LSP Integration** | ✅ 25+ languages, auto-discovery | ✅ 11 languages (added Dec 2025) |
| **Pricing** | ✅ Pay-as-you-go or BYO keys | ❌ Subscription tiers ($20-$200/mo) |
| **Plugin System** | ✅ Extensible hooks & MCP | ⚠️ Limited |
| **Architecture** | ✅ Client/Server (flexible clients) | ❌ Terminal-only |
| **Self-Hosting** | ✅ Fully supported | ❌ Cloud-only |
| **Provider Agnostic** | ✅ Yes | ❌ No (vendor lock-in) |

**Key Differentiators**:
- **Freedom**: Not tied to Anthropic ecosystem; use any provider
- **Cost**: Bring your own keys or use OpenCode Zen's competitive pricing
- **Extensibility**: Plugin system allows deep customization and integrations
- **Flexibility**: Client/server architecture enables remote control and multiple client types
- **Transparency**: 100% open source with community-driven development

### vs. Cursor

| Feature | OpenCode | Cursor |
|---------|----------|--------|
| **Open Source** | ✅ 100% MIT License | ❌ Proprietary ($500M ARR) |
| **Terminal First** | ✅ Built for terminal workflows | ⚠️ IDE-based (VS Code fork) |
| **Multi-Model** | ✅ 75+ providers | ✅ GPT-5, Claude 4.5, Gemini 3, Grok |
| **LSP Support** | ✅ 25+ languages, auto-discovery | ✅ Via IDE |
| **Pricing** | ✅ Free + BYO keys or Zen | ❌ $20/month Pro |
| **Self-Hosting** | ✅ Fully supported | ❌ Cloud-only |
| **Plugin System** | ✅ Extensible with hooks & MCP | ⚠️ Limited IDE extensions |
| **Architecture** | ✅ Client/Server | ❌ Desktop IDE only |

**Key Differentiators**:
- **Cost**: OpenCode is free (BYO keys) vs. Cursor's $20/month mandatory subscription
- **Terminal Excellence**: Built by neovim users, optimized for terminal workflows
- **Freedom**: No vendor lock-in, true open source with full control
- **Self-Hosting**: Deploy on-premises for privacy and compliance

---

## 🎯 Target Markets

### Primary Market

**Individual Developers & Freelancers**
- Early adopters of AI tools who value transparency and control
- Terminal-first developers (vim/neovim users, CLI enthusiasts)
- Cost-conscious developers wanting to avoid subscription lock-in
- Privacy-conscious developers needing self-hosting options

### Secondary Market

**Small Teams & Startups (5-50 employees)**
- Teams needing a unified AI development platform across multiple providers
- Startups with compliance requirements requiring self-hosting
- Teams building custom integrations and workflows via plugins
- Organizations wanting to avoid vendor lock-in and long-term contracts

### Tertiary Market

**Enterprise & Mid-Large Companies (50+ employees)**
- Enterprises with strict data governance and security requirements
- Organizations needing multi-tenant console with per-seat licensing
- Companies building AI-powered internal developer tools
- Government and regulated industries requiring air-gapped deployments

---

## 🌟 Product Highlights

### Technical Excellence

**Performance**
- Bun runtime for lightning-fast JavaScript execution
- Async I/O for non-blocking operations
- Worker threads to prevent UI blocking
- Intelligent caching and token optimization
- Session compaction to manage memory efficiently

**Architecture**
- Client/server design for flexibility and scalability
- Modular monorepo with 15 specialized packages
- TypeScript for type safety and maintainability
- Tauri v2 + Rust for desktop performance
- SolidJS for reactive UI components

**AI Capabilities**
- AI SDK integration for 75+ providers
- Multi-agent orchestration with specialized roles
- Aggressive parallel task execution
- Background agent delegation
- Todo-driven workflows for complex tasks
- LSP-integrated code intelligence

**Developer Experience**
- Zero screen flicker with OpenTUI framework
- Keyboard-driven interface with customizable keybinds
- Split-view for code, files, and terminal
- Real-time syntax highlighting
- File explorer with project tree view
- Mouse support when needed

### Ecosystem

**OpenCode Zen**
- Curated, tested models optimized for coding
- Competitive pricing: GPT 5.1 ($1.75/$14.00), Claude Sonnet 4.5 ($3.00/$15.00), Ge
