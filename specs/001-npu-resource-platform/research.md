# 研究记录: 昇腾 NPU 资源管理平台

**Created**: 2026-01-12  
**Scope**: 控制面与数据面架构、预约冲突规则、监控采集与审计策略

## 决策 1: 控制面与数据面解耦方式

- **Decision**: 采用控制面服务 + 服务器本地代理（ServerSentinel），代理长连接/轮询拉取授权变更。
- **Rationale**: 控制面宕机时不影响已建立的 SSH 会话，代理在本地独立执行授权更新。
- **Alternatives considered**: 控制面直接推送并写入远程 authorized_keys；人工运维手动变更。

## 决策 2: 预约冲突判定规则

- **Decision**: 时间窗按秒精度，区间为 [start, end)；任意 1 秒重叠视为冲突。
- **Rationale**: 与验收标准一致，规则简单且可在数据库层做一致性约束。
- **Alternatives considered**: 以分钟为粒度；允许 1 秒重叠的“宽容”模式。

## 决策 3: 预约模式与卡选择

- **Decision**: 整机模式占用全机；拼车模式占用单卡，预约请求需指定 card_index。
- **Rationale**: 与“锁住 Card-0，其他人可申请 Card-1”的需求一致，可扩展到任意卡。
- **Alternatives considered**: 拼车固定只支持 Card-0；拼车由系统自动分配卡。

## 决策 4: 身份与登录策略

- **Decision**: 默认本地白名单账号+密码登录；LDAP 可选；SSH 登录账号与 Web 登录账号一致。
- **Rationale**: 降低部署成本，同时保留企业 LDAP 对接能力。
- **Alternatives considered**: 仅 LDAP 登录；团队共享账号。

## 决策 5: 存储与一致性

- **Decision**: 默认使用 SQLite；支持 PostgreSQL/MySQL 作为可选部署。
- **Rationale**: 本地部署成本低，同时保留强一致事务数据库选项。
- **Alternatives considered**: 仅 PostgreSQL；仅 SQLite。

## 决策 6: 指标采集与刷新节奏

- **Decision**: 代理每 15 秒采集一次 npu-smi 指标，控制面/前端 30 秒内刷新。
- **Rationale**: 满足 <30 秒刷新要求，并兼顾负载与实时性。
- **Alternatives considered**: 5 秒高频采集；60 秒低频采集。

## 决策 7: 审计报表导出格式

- **Decision**: 默认导出 CSV，支持按时间窗筛选。
- **Rationale**: 便于财务核算与跨系统导入。
- **Alternatives considered**: 仅 JSON；PDF 报表。

## 决策 8: 时间与时区标准

- **Decision**: 所有预约与报表使用系统默认时区（Asia/Shanghai），存储为 UTC 时间戳。
- **Rationale**: 内部团队单一时区，可减少混乱并保持后端一致性。
- **Alternatives considered**: 仅 UTC 展示；用户自选时区。
