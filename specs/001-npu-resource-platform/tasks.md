---

description: "Task list template for feature implementation"
---

# Tasks: 昇腾 NPU 资源管理平台

**Input**: Design documents from `/specs/001-npu-resource-platform/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/
**Doc Language**: 中文为主（如需双语，先中文后英文）

**Tests**: 规格未明确要求测试任务，本清单不列出测试任务（如需补充测试，请在后续任务中添加）。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `agent/` at repository root
- Paths shown below align with plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per plan using .gitkeep in backend/cmd/api/.gitkeep, backend/internal/.gitkeep, agent/cmd/sentinel/.gitkeep, frontend/src/.gitkeep
- [ ] T002 Initialize backend FastAPI project in backend/pyproject.toml and backend/cmd/api/main.py
- [ ] T003 Initialize agent Python project in agent/pyproject.toml and agent/cmd/sentinel/main.py
- [ ] T004 Initialize frontend React/Vite scaffold in frontend/package.json, frontend/vite.config.ts, frontend/src/main.tsx
- [ ] T005 Add environment templates in backend/.env.example, agent/.env.example, frontend/.env.example
- [ ] T006 Configure lint/format in backend/pyproject.toml, frontend/eslint.config.js, frontend/.prettierrc

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Setup settings and DB session in backend/internal/config/settings.py, backend/internal/db/session.py
- [ ] T008 Create SQLAlchemy base and model package in backend/internal/db/base.py, backend/internal/db/models/__init__.py
- [ ] T009 Implement core models in backend/internal/db/models/user.py, team.py, server.py, npu_card.py, reservation.py, metric_snapshot.py, audit_log.py, alert.py
- [ ] T010 Add Alembic config and initial migration in backend/alembic.ini, backend/alembic/env.py, backend/alembic/versions/0001_initial.py
- [ ] T011 Implement LDAP auth client and whitelist lookup in backend/internal/auth/ldap.py, backend/internal/auth/service.py
- [ ] T012 Implement auth dependencies and admin guard in backend/internal/auth/deps.py, backend/internal/auth/permissions.py
- [ ] T013 Build FastAPI app and router registry in backend/cmd/api/main.py, backend/internal/api/router.py
- [ ] T014 Add API error handling and logging middleware in backend/internal/api/middleware.py, backend/internal/api/errors.py
- [ ] T015 Implement reservation validation utilities in backend/internal/reservation/validators.py, backend/internal/reservation/conflict.py
- [ ] T016 Create background scheduler harness in backend/internal/jobs/scheduler.py
- [ ] T017 Add agent API router module in backend/internal/agent/routes.py and register in backend/internal/api/router.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - 预约与准入控制 (Priority: P1) 🎯 MVP

**Goal**: 用户可登录、上传 SSH 公钥、查看可用资源并完成预约，预约生效时获得访问权限。

**Independent Test**: 白名单用户上传公钥后可成功预约并在预约时段内 SSH 登录，时段外被拒绝。

### Implementation for User Story 1

- [ ] T018 [US1] Implement login endpoint /auth/login in backend/internal/auth/routes.py
- [ ] T019 [US1] Implement /me and /me/ssh-key endpoints in backend/internal/auth/routes.py
- [ ] T020 [US1] Implement server availability list /servers in backend/internal/inventory/routes.py
- [ ] T021 [US1] Implement reservation business rules in backend/internal/reservation/service.py
- [ ] T022 [US1] Implement /reservations create/list/cancel in backend/internal/reservation/routes.py
- [ ] T023 [US1] Implement reservation activation/expiration jobs in backend/internal/reservation/jobs.py
- [ ] T024 [US1] Implement access policy API for agents in backend/internal/agent/routes.py
- [ ] T025 [US1] Implement agent policy cache/polling in agent/internal/access/sync.py
- [ ] T026 [US1] Implement authorized_keys updater in agent/internal/access/authorized_keys.py
- [ ] T027 [US1] Wire access control workflow in agent/cmd/sentinel/main.py
- [ ] T028 [US1] Build login flow in frontend/src/services/auth.ts, frontend/src/pages/Login.tsx
- [ ] T029 [US1] Build SSH key management UI in frontend/src/pages/Profile.tsx, frontend/src/services/user.ts
- [ ] T030 [US1] Build reservation UI in frontend/src/pages/Reservation.tsx, frontend/src/services/reservations.ts
- [ ] T031 [US1] Add carpool env hint modal in frontend/src/components/ReservationSuccessModal.tsx
- [ ] T032 [US1] Disable reservation when no SSH key in frontend/src/pages/Reservation.tsx

**Checkpoint**: User Story 1 should be functional and independently verifiable

---

## Phase 4: User Story 2 - 资源状态与监控可视化 (Priority: P2)

**Goal**: 用户可通过矩阵视图与指标面板实时查看资源状态与异常。

**Independent Test**: 首页矩阵展示红绿灯状态，指标每 30 秒刷新且异常高亮。

### Implementation for User Story 2

- [ ] T033 [US2] Implement metrics ingestion endpoint in backend/internal/metrics/routes.py
- [ ] T034 [US2] Implement metrics persistence in backend/internal/metrics/service.py
- [ ] T035 [US2] Implement dashboard summary /dashboard/summary in backend/internal/metrics/summary.py
- [ ] T036 [US2] Implement anomaly detection rules in backend/internal/metrics/alerts.py
- [ ] T037 [US2] Implement alerts list /alerts in backend/internal/metrics/routes.py
- [ ] T038 [US2] Implement npu-smi parser in agent/internal/metrics/parser.py
- [ ] T039 [US2] Implement periodic metrics collector in agent/internal/metrics/collector.py
- [ ] T040 [US2] Implement agent heartbeat reporting in agent/internal/heartbeat/client.py
- [ ] T041 [US2] Build matrix dashboard in frontend/src/pages/Dashboard.tsx, frontend/src/components/ServerMatrix.tsx
- [ ] T042 [US2] Build metrics panel with refresh in frontend/src/components/MetricsPanel.tsx, frontend/src/services/metrics.ts
- [ ] T043 [US2] Highlight anomaly alerts in frontend/src/components/AlertBadge.tsx, frontend/src/services/alerts.ts

**Checkpoint**: User Story 2 should be functional and independently verifiable

---

## Phase 5: User Story 3 - 管理员治理与审计 (Priority: P3)

**Goal**: 管理员可维护白名单、服务器入库/发现、强制释放与审计导出。

**Independent Test**: 管理员完成白名单录入、强制释放与审计导出流程。

### Implementation for User Story 3

- [ ] T044 [US3] Extend API contract for admin endpoints in specs/001-npu-resource-platform/contracts/openapi.yaml
- [ ] T045 [US3] Implement whitelist admin endpoints in backend/internal/auth/admin_routes.py
- [ ] T046 [US3] Implement server add/discover endpoints in backend/internal/inventory/admin_routes.py
- [ ] T047 [US3] Implement topology discovery service in backend/internal/inventory/discovery.py
- [ ] T048 [US3] Implement force-release endpoint in backend/internal/reservation/admin_routes.py
- [ ] T049 [US3] Implement audit logging middleware in backend/internal/audit/middleware.py and backend/internal/audit/service.py
- [ ] T050 [US3] Implement audit log list/export in backend/internal/audit/routes.py
- [ ] T051 [US3] Implement audit retention job in backend/internal/audit/retention.py
- [ ] T052 [US3] Implement alert resolve endpoint in backend/internal/metrics/admin_routes.py
- [ ] T053 [US3] Build whitelist admin UI in frontend/src/pages/AdminUsers.tsx, frontend/src/services/admin.ts
- [ ] T054 [US3] Build server admin UI in frontend/src/pages/AdminServers.tsx, frontend/src/services/servers.ts
- [ ] T055 [US3] Build force-release UI in frontend/src/components/ForceReleaseButton.tsx
- [ ] T056 [US3] Build audit export UI in frontend/src/pages/AuditLogs.tsx, frontend/src/services/audit.ts
- [ ] T057 [US3] Build alert resolve UI in frontend/src/components/AlertResolveButton.tsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T058 Update quickstart to Python/FastAPI/agent in specs/001-npu-resource-platform/quickstart.md
- [ ] T059 Add API rate limit for auth/reservation in backend/internal/api/middleware.py
- [ ] T060 Add metrics retention cleanup in backend/internal/metrics/retention.py
- [ ] T061 Validate quickstart steps and update notes in specs/001-npu-resource-platform/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
Task: "Implement login endpoint /auth/login in backend/internal/auth/routes.py"
Task: "Build login flow in frontend/src/services/auth.ts, frontend/src/pages/Login.tsx"
Task: "Implement authorized_keys updater in agent/internal/access/authorized_keys.py"
```

---

## Parallel Example: User Story 2

```bash
Task: "Implement npu-smi parser in agent/internal/metrics/parser.py"
Task: "Build matrix dashboard in frontend/src/pages/Dashboard.tsx, frontend/src/components/ServerMatrix.tsx"
Task: "Implement dashboard summary /dashboard/summary in backend/internal/metrics/summary.py"
```

---

## Parallel Example: User Story 3

```bash
Task: "Implement audit log list/export in backend/internal/audit/routes.py"
Task: "Build audit export UI in frontend/src/pages/AuditLogs.tsx, frontend/src/services/audit.ts"
Task: "Implement topology discovery service in backend/internal/inventory/discovery.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Use manual verification for User Story 1
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Validate independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Validate independently → Deploy/Demo
4. Add User Story 3 → Validate independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
