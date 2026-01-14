# 快速开始: 昇腾 NPU 资源管理平台

**Created**: 2026-01-12

## 前置条件

- Linux 服务器用于控制面与代理运行
- Node.js 18+（前端开发）
- Python 3.11+（控制面与代理）
- PostgreSQL 16

## 本地开发启动（示例）

仓库根目录：`/Users/eric/Workspaces/Github/ServerDispatch`

### 1) 启动数据库

- 创建数据库与用户，确保控制面可连接。

### 2) 启动控制面

```bash
cd /Users/eric/Workspaces/Github/ServerDispatch/backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg[binary] pydantic pydantic-settings ldap3 python-jose[cryptography]
cp .env.example .env
python -m uvicorn cmd.api.main:app --reload --port 8000
```

### 3) 启动前端

```bash
cd /Users/eric/Workspaces/Github/ServerDispatch/frontend
npm install
npm run dev
```

### 4) 启动服务器代理（示例）

```bash
cd /Users/eric/Workspaces/Github/ServerDispatch/agent
python -m venv .venv
source .venv/bin/activate
pip install pydantic pydantic-settings
python -m cmd.sentinel.main --server-ip 10.0.0.1 --access-account admin
```

## 备注

- 控制面与代理均使用 Python；如需调整依赖版本，请以 `backend/pyproject.toml` 为准。
- 代理启动示例为占位，需确保 agent 端实现可执行入口后再运行。

## 验证路径

1. 管理员创建 LDAP 白名单用户并为其上传 SSH 公钥。
2. 在首页矩阵中查看服务器与卡的状态颜色。
3. 创建预约并确认 SSH 权限在 1 秒内生效，结束时 1 秒内撤销。
4. 仪表盘每 30 秒刷新一次 NPU 指标。
