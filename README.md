# Taskflow：LangChain + MCP + MySQL

使用 LangChain Agent 管理 items：模型调用 MCP 工具，MCP 将请求交给 FastAPI，SQLAlchemy 将业务数据存入 MySQL。保留 `/api/items/` 增删改查接口和 `/mcp` SSE 接口。LangChain 使用 `create_agent` 和 `langchain-mcp-adapters`。

## 启动

需要 Python 3.13、uv 和 Docker Compose。

```bash
cp .env.example .env
# 编辑 .env，修改数据库密码；运行智能体时填写 OPENAI_API_KEY
uv sync
# 首次生成 uv.lock 后应提交版本控制；后续安装可用 uv sync --locked
docker compose up -d --build
```

API 文档：http://localhost:8000/docs 。数据库数据存入 `mysql_data` Docker volume。
API 服务不需要模型密钥；模型仅在运行客户端时调用。

本地开发也可只启动数据库：

```bash
docker compose up -d mysql
uv run uvicorn backend.server.main:app --reload
```

`.env` 默认连接本机 MySQL，Compose 中服务使用内部主机名 `mysql`。
如使用已有数据库，配置 `MYSQL_HOST/PORT/DATABASE/USER/PASSWORD`，或通过
`DATABASE_URL=mysql+pymysql://...` 覆盖连接串。单独的密码字段支持特殊字符；
连接串中的密码需要 URL 编码。数据库必须预先存在，服务在启动时创建缺失的数据表。
`create_all` 不会升级已有表，后续表结构变更需要正式的数据库迁移。

## 运行 LangChain 智能体

先启动 API，再执行：

```bash
uv run python -m backend.client.main
```

配置 `LLM_MODEL=openai:gpt-4o-mini`、`OPENAI_API_KEY`，可选 `OPENAI_BASE_URL`。
当前依赖包含 OpenAI 集成；使用其他供应商需要安装对应的 LangChain 集成包。
`MCP_HOST_URL` 默认为 `http://127.0.0.1:8000/mcp`，`MCP_TRANSPORT=sse` 与当前
FastAPI-MCP 服务对应。客户端从 MCP 加载工具，依次执行创建、查询、更新、读取和删除，
共享消息历史以使用实际创建的 ID。模型调用需要网络和有效密钥。

## 测试

测试使用 MySQL，与应用保持一致。先创建独立数据库 `taskflow_test` 并为测试账号授权，
再执行以下命令（测试会删除并重建该库中的 `items` 表）：

```bash
TEST_DATABASE_URL='mysql+pymysql://user:password@127.0.0.1:3306/taskflow_test?charset=utf8mb4' uv run pytest
```

测试库名称必须以 `_test` 结尾。不设置 `TEST_DATABASE_URL` 时，仅运行无需数据库的
配置及 DDL 测试，数据库测试会跳过。CI 提供 MySQL 8.4 服务并运行完整测试。
测试覆盖 CRUD、分页、中文输入、字段长度和 MySQL 建表语句，不需要模型密钥。

## 目录

- `backend/config.py`：环境变量和 MySQL 连接配置
- `backend/server/`：FastAPI、MCP、ORM 和 CRUD
- `backend/client/`：LangChain Agent 和场景
- `tests/`：API、配置与 MySQL 测试
- `PROJECT_GUIDE_ZH.md`：架构与开发说明
