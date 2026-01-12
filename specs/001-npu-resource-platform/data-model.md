# 数据模型: 昇腾 NPU 资源管理平台

**Created**: 2026-01-12

## 实体与字段

### User

- id
- ldap_id（唯一）
- ssh_login（与 Web 登录一致）
- ssh_public_key
- display_name
- team_id
- status（active/disabled）
- created_at
- updated_at

### Team

- id
- name（唯一）
- created_at
- updated_at

### Server

- id
- hostname
- ip（唯一）
- access_account（用于入库与拓扑发现）
- status（online/offline/unknown）
- model（910B/310）
- card_count
- chip_id
- hbm_gb
- created_at
- updated_at

### NPUCard

- id
- server_id
- index（0..card_count-1）
- status（free/occupied/offline）
- current_reservation_id

### Reservation

- id
- user_id
- server_id
- card_id（拼车必填，整机为空）
- mode（full_machine/carpool）
- start_time
- end_time
- status（scheduled/active/completed/canceled/forced_release）
- created_at
- updated_at

### MetricSnapshot

- id
- server_id
- card_id
- timestamp
- ai_core_util
- hbm_used
- hbm_total
- temperature

### AuditLog

- id
- actor_user_id
- action_type
- target_type
- target_id
- timestamp
- metadata

### Alert

- id
- server_id
- card_id
- type（no_reservation_high_load/reservation_zero_load）
- status（open/resolved）
- detected_at
- resolved_at

## 关系

- Team 1..N User
- Server 1..N NPUCard
- User 1..N Reservation
- Reservation 1..1 Server
- Reservation 0..1 NPUCard（整机模式为空）
- Server 1..N MetricSnapshot
- NPUCard 1..N MetricSnapshot
- User 1..N AuditLog（actor）

## 约束与校验规则

- ldap_id 唯一且必须存在于管理员维护的白名单中。
- Reservation 时间窗以秒为精度，区间 [start_time, end_time)。
- 任意预约时间窗不得与已有预约存在 1 秒重叠。
- full_machine 模式占用全机并阻断所有该机的卡预约。
- carpool 模式必须指定 card_id。
- 服务器离线时禁止创建预约。

## 状态流转

### Reservation

- scheduled -> active（到达开始时间）
- scheduled -> canceled（用户取消）
- active -> completed（到达结束时间）
- active -> forced_release（管理员强制释放）

### Alert

- open -> resolved（异常解除或管理员确认）
