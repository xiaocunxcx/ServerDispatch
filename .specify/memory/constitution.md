<!--
Sync Impact Report
- Version change: N/A (template) -> 1.0.0
- Modified principles: PRINCIPLE_1_NAME -> I. 代码质量优先; PRINCIPLE_2_NAME -> II. 测试标准（不可协商）; PRINCIPLE_3_NAME -> III. 用户体验一致性; PRINCIPLE_4_NAME -> IV. 性能要求明确且可验证; PRINCIPLE_5_NAME -> V. 文档中文优先
- Added sections: 性能标准; 交付流程与文档语言
- Removed sections: None
- Templates requiring updates: ✅ .specify/templates/plan-template.md; ✅ .specify/templates/spec-template.md; ✅ .specify/templates/tasks-template.md; ⚠ .specify/templates/commands/*.md (directory not found)
- Follow-up TODOs: TODO(RATIFICATION_DATE): 原始批准日期未知，需要补充
-->
# ServerDispatch Constitution

## Core Principles

### I. 代码质量优先
- 所有变更必须通过格式化、静态检查与构建质量门禁，不允许绕过。
- 禁止引入死代码、未使用依赖或临时性实现；如需过渡方案，必须在任务中记录替换计划。
- 复杂逻辑必须可读、可维护，必要时拆分并补充最小化说明。
理由: 代码质量直接影响可维护性、交付速度与缺陷率。

### II. 测试标准（不可协商）
- 新增或修改的业务逻辑必须配套自动化测试，覆盖关键路径与边界条件。
- 缺陷修复必须新增回归测试，防止同类问题复现。
- 测试必须可重复、可预测；CI 中任何测试失败都阻断合并。
理由: 可验证的测试是稳定迭代与风险控制的最低保障。

### III. 用户体验一致性
- 用户可见的交互、文案与信息架构必须与既有体验保持一致，避免无理由的差异。
- 复用现有组件与交互规范；如需新增模式，必须在文档中明确并同步更新。
- 任何影响用户体验的变更必须可验证（验收场景或演示）。
理由: 一致性减少认知负担并提升用户信任。

### IV. 性能要求明确且可验证
- 所有面向用户或关键路径的改动必须定义可度量的性能指标与验证方式。
- 不允许引入超过约定阈值的性能回归；必要时提供基准测试或剖析报告。
- 资源使用（延迟、吞吐、内存、启动时间）需在设计中明确预算。
理由: 性能是用户体验与系统成本的核心约束。

### V. 文档中文优先
- 所有新文档与更新必须优先使用中文撰写。
- 如需双语版本，中文为权威版本，英文为辅并保持同步。
理由: 统一语言降低沟通成本并确保信息一致。

## 性能标准

- 在每份 feature 规格中必须明确性能目标、测量方法与回归阈值。
- 对关键路径或高负载场景必须提供基准测试或可复现的测量脚本。
- 性能不达标时，必须在计划中明确优化路径或降级策略。

## 交付流程与文档语言

- 所有变更必须经过同伴评审，评审人需确认代码质量、测试覆盖、UX 一致性与性能要求。
- 合并前必须提供测试结果与验证说明；若无法自动化，需记录原因与风险。
- 规划与交付文档以中文为主，模板与产出需遵循此约束。

## Governance
- 本宪章优先级最高，若与其他流程冲突，以本宪章为准。
- 修订流程: 提交修订提案 → 评审达成共识 → 记录变更原因与影响范围 → 更新版本号与日期。
- 版本规则: 重大原则变更为 MAJOR，新原则或新增约束为 MINOR，文字澄清为 PATCH。
- 每次 PR/评审必须进行宪章符合性检查并记录结果。

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): 原始批准日期未知 | **Last Amended**: 2026-01-12
