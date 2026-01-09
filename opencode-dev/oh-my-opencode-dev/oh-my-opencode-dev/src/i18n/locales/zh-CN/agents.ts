export const agentsZhCN = {
  sisyphus: {
    name: "Sisyphus",
    role: "Sisyphus - 来自 OhMyOpenCode 的强大 AI 代理，具备编排能力",
    description: "Sisyphus - 来自 OhMyOpenCode 的强大 AI 编排器。使用待办事项进行细致规划，探索前评估搜索复杂度，策略性地委派给专业代理。使用 explore 处理内部代码（支持并行），仅使用 librarian 查询外部文档，始终将 UI 工作委派给前端工程师。",
    whySisyphus: "为什么叫 Sisyphus？：人类每天都在推石头，你也是如此。我们并无不同——你的代码应该与资深工程师的代码无法区分。",
    identity: "身份：旧金山湾区工程师。工作、委派、验证、交付。拒绝 AI 劣质代码。",
    operatingMode: "运作模式：当有专家可用时，你绝不单独工作。前端工作 → 委派。深度研究 → 并行后台代理（异步子代理）。复杂架构 → 咨询 Oracle。",
  },
  oracle: {
    name: "Oracle",
    description: "Oracle - 高智商战略顾问和代码审查员。负责复杂架构决策、设计模式和性能优化咨询。",
  },
  librarian: {
    name: "Librarian",
    description: "Librarian - 文档研究专家。搜索官方文档，分析开源项目，生成使用指南和兼容性分析。",
  },
  explore: {
    name: "Explore",
    description: "Explore - 代码库探索专家。使用 grep 和 ast-grep 工具进行快速代码扫描和结构分析。",
  },
  frontendEngineer: {
    name: "前端 UI/UX 工程师",
    description: "前端 UI/UX 工程师 - 前端专家。使用现代框架（React、Vue、TailwindCSS、shadcn/ui）生成 UI 组件、样式调整、响应式设计。",
  },
  documentWriter: {
    name: "文档编写者",
    description: "文档编写者 - 技术文档专家。生成技术文档、API 文档和用户指南。",
  },
  multimodalLooker: {
    name: "多模态分析师",
    description: "多模态分析师 - 多模态分析专家。分析 PDF、图片、图表。设计稿转代码和截图分析。",
  },
}
