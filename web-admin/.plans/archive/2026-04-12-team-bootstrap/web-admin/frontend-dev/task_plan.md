# frontend-dev - 任务计划

> 角色: 前端开发工程师
> 状态: in_progress
> 分配的任务: T3 — Vue 3 脚手架 + 登录页 + 路由守卫

## 任务

- [ ] T3: Vue 3 项目搭建 + 登录页（与 T1 并行执行）
  - [ ] 在 web-admin/frontend/ 初始化 Vite + Vue 3 项目
  - [ ] 配置 Element Plus + Pinia + Vue Router + Axios
  - [ ] 使用 ui-ux-pro-max skill 确定设计风格（Swiss 或 Minimalist archetype）
  - [ ] 建立 CSS 设计 tokens（颜色、间距、字体）
  - [ ] 实现登录页（对接 POST /api/auth/login）
  - [ ] 配置路由守卫（JWT token 检查，未登录跳转到 /login）
  - [ ] 配置 Axios 拦截器（自动携带 Token，处理 401 跳转）
  - [ ] SendMessage(to: "team-lead") 汇报完成

## 备注

- 工作目录：G:\py\aiweb\web-admin\frontend\
- API 接口参考：.plans/web-admin/docs/api-contracts.md §Auth API
- 技术栈：Vue 3 + Element Plus + Vite + Pinia + Vue Router + Axios
- 前端技能策略：默认使用 `ui-ux-pro-max`，后续所有 UI/UX 任务保持一致
- 设计参考：ui-ux-pro-max skill（管理后台适合 Swiss/Minimalist 风格）
- 可与 T1（researcher）并行执行，不依赖后端实现（先 Mock 数据）

