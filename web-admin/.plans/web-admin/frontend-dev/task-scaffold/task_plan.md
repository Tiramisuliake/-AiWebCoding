# task-scaffold — 详细步骤计划

> 目标：搭建 Vue 3 前端项目，实现登录页和路由权限守卫
> 状态: in_progress
> 开始时间: 2026-04-12

## 设计决策（ui-ux-pro-max 方法论）

### Step 1: Context Analysis
- 管理后台（Admin Dashboard）
- 目标用户：系统管理员，长时间使用
- 需求：高信息密度、清晰层次、减少视觉疲劳
- 功能：登录、用户管理、角色管理、权限管理

### Step 2: Archetype Selection
- 选择：**Swiss**（国际主义风格）
- 理由：网格严谨、排版精确，适合数据密集型后台，比 Minimalist 更有结构感

### Step 3: Differentiator
- **核心差异点**：用左侧垂直彩色标记线（4px accent border）区分菜单层级，配合精确的 8px 基础网格，让信息层次一目了然

### Step 4: Tokens（见 findings.md）

### Step 5: Implementation
- 严格执行 Swiss 风格，不折中

---

## 执行步骤

- [x] 创建任务文件夹
- [x] 在根 findings.md 添加索引
- [ ] 初始化 Vite + Vue 3 项目
- [ ] 安装依赖（Element Plus、Pinia、Vue Router、Axios）
- [ ] 建立目录结构
- [ ] 创建 design-tokens.css
- [ ] 配置 Element Plus
- [ ] 配置 Vue Router（含路由守卫）
- [ ] 配置 Pinia useAuthStore
- [ ] 配置 Axios 拦截器（request.js + auth.js）
- [ ] 实现 LoginView.vue
- [ ] 实现 DashboardView.vue
- [ ] 更新 findings.md（archetype + tokens 记录）
- [ ] 更新根 findings.md（Status: complete）
- [ ] SendMessage(to: "team-lead") 汇报完成

