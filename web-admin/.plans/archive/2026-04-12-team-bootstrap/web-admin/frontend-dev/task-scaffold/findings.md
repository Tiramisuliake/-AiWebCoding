# task-scaffold — 发现记录

## 设计系统决策

### Archetype: Swiss（国际主义风格）
理由：管理后台需要高信息密度 + 清晰网格结构，Swiss 风格比 Minimalist 更有结构感，适合长时间使用的数据密集型界面。

### Differentiator
**左侧 4px accent border + 8px 基础网格**
- 菜单激活项左侧显示 4px 蓝色标记线，提供视觉锚点
- 所有间距基于 8px 网格（8, 16, 24, 32, 40, 48px）
- 字体用 Inter 或系统无衬线字体，行高精确控制

### CSS Design Tokens（src/assets/design-tokens.css）

```css
/* 颜色 */
--color-primary: #2563EB;        /* Swiss blue - 主操作色 */
--color-primary-light: #EFF6FF;  /* 浅蓝背景 */
--color-primary-dark: #1D4ED8;   /* Hover 状态 */
--color-accent: #2563EB;         /* 4px 左侧标记线 */
--color-bg: #F8FAFC;             /* 页面背景 */
--color-surface: #FFFFFF;        /* 卡片/面板背景 */
--color-border: #E2E8F0;         /* 边框色 */
--color-text-primary: #0F172A;   /* 主文本 */
--color-text-secondary: #64748B; /* 次要文本 */
--color-text-disabled: #CBD5E1;  /* 禁用文本 */
--color-error: #DC2626;          /* 错误状态 */
--color-success: #16A34A;        /* 成功状态 */
--color-warning: #D97706;        /* 警告状态 */
--color-aside-bg: #1E293B;       /* 侧边栏背景（深色） */
--color-aside-text: #CBD5E1;     /* 侧边栏文本 */
--color-aside-active: #2563EB;   /* 侧边栏激活背景 */

/* 间距（8px 网格） */
--space-1: 8px;
--space-2: 16px;
--space-3: 24px;
--space-4: 32px;
--space-5: 40px;
--space-6: 48px;

/* 字体 */
--font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-base: 16px;
--font-size-lg: 18px;
--font-size-xl: 24px;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--line-height-tight: 1.25;
--line-height-base: 1.5;

/* 圆角（Swiss 风格偏向锐角，小圆角） */
--radius-sm: 2px;
--radius-base: 4px;
--radius-lg: 6px;

/* 阴影 */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-base: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);

/* 过渡 */
--transition-base: 150ms ease;

/* 布局 */
--aside-width: 220px;
--header-height: 56px;
--accent-border-width: 4px;    /* Swiss differentiator */
```

## 技术发现

（开发中记录）
