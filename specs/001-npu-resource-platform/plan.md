# Implementation Plan: 昇腾 NPU 资源管理平台

**Branch**: `001-npu-resource-platform` | **Date**: 2026-01-12 | **Spec**: /Users/eric/Workspaces/Github/ServerDispatch/specs/001-npu-resource-platform/spec.md
**Input**: Feature specification from `/specs/001-npu-resource-platform/spec.md`
**Doc Language**: 中文为主（如需双语，先中文后英文）

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

为昇腾 NPU 集群提供统一的资源可视化、预约与动态 SSH 门禁平台，
通过 FastAPI 控制面 + 服务器本地代理实现准入控制、监控与审计。

## Technical Context

**Language/Version**: Python 3.11（控制面与代理）; TypeScript 5.4（前端）  
**Primary Dependencies**: FastAPI, SQLAlchemy, Alembic, Pydantic, React, Vite  
**Storage**: PostgreSQL 16  
**Testing**: pytest, pytest-asyncio, Vitest, Playwright（关键路径 UI）  
**Target Platform**: Linux 服务器（控制面与代理），现代浏览器（Web UI）
**Project Type**: web（frontend + backend + agent）  
**Performance Goals**: 权限启停 ≤ 1 秒；指标刷新 ≤ 30 秒；支持 50 台服务器、200 用户  
**Constraints**: 控制面重启不影响已建立 SSH；时间窗精度到秒；审计日志保留 ≥ 30 天  
**Scale/Scope**: 10-50 台服务器（2-8 卡/台），100-1000 个预约/月

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] 代码质量门禁已明确（格式化、静态检查、代码可维护性）
- [x] 测试标准已定义（覆盖范围、关键路径、回归测试要求）
- [x] 用户体验一致性已对齐（组件/文案规范、验收方式）
- [x] 性能指标与回归阈值已定义（测量方法明确）
- [x] 文档语言为中文优先（如需双语，中文为权威）

## Project Structure

### Documentation (this feature)

```text
specs/001-npu-resource-platform/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── cmd/
│   └── api/
├── internal/
│   ├── auth/
│   ├── reservation/
│   ├── inventory/
│   ├── metrics/
│   └── audit/
└── tests/

agent/
├── cmd/
│   └── sentinel/
├── internal/
│   ├── access/
│   ├── metrics/
│   └── heartbeat/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── styles/
└── tests/
```

**Structure Decision**: 采用前后端分离 + 本地代理的结构，
控制面负责预约与审计，代理负责 SSH 门禁与 NPU 指标采集。

## Complexity Tracking

无违反项。

## Constitution Check (Post-Design)

- [x] 代码质量与测试门禁在计划中已落实
- [x] UX 一致性与验收方式已明确
- [x] 性能与可验证指标已明确
- [x] 文档语言与交付流程符合宪章
