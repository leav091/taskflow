# Taskflow 开发说明

## 架构

Taskflow 由 LangChain 智能体客户端、FastAPI/MCP 服务和 MySQL 数据库组成。

```mermaid
flowchart LR
    User[自然语言场景] --> Agent[LangChain Agent]
    Agent --> MCP[MCP 工具]
    MCP --> API[FastAPI CRUD]
    API --> ORM[SQLAlchemy]
    ORM --> DB[(MySQL)]
```

## 服务端

`backend/config.py` 使用 Pydantic Settings 读取环境变量及 `.env`，构造
`mysql+pymysql` 连接。分字段配置通过 SQLAlchemy URL 处理密码中的特殊字符。

`backend/server/db.py` 创建连接池和会话工厂。每个请求独立获取会话，失败时回滚，
结束时关闭。连接启用 `pool_pre_ping`，降低数据库空闲连接断开带来的影响。

`backend/server/models.py` 定义 `items` 表及请求、响应模型：

| 字段 | 数据库类型 | 用途 |
| --- | --- | --- |
| id | Integer，主键 | 记录标识 |
| name | VARCHAR(255)，非空 | 名称 |
| description | TEXT，可空 | 描述 |

`backend/server/crud.py` 实现数据库操作，列表按 ID 排序后分页。
`backend/server/routes.py` 提供 `/api/items/` 下的五个 CRUD 接口。
`backend/server/main.py` 在应用启动时创建缺失的表，并将接口暴露为 `/mcp` SSE 工具。
数据库必须提前创建，`create_all` 仅用于首次建表，表结构升级需要单独管理。

## 智能体客户端

`backend/client/main.py` 使用 `MultiServerMCPClient` 加载 MCP 工具，
通过 `init_chat_model` 初始化模型，再用 `create_agent` 构造 LangChain 智能体。
执行场景时共享消息历史，使后续操作能够引用实际创建的记录 ID。

`backend/client/scenarios.py` 定义创建、列表、更新、读取及删除场景。
客户端需要有效的模型密钥；仅运行 API 和数据库测试不需要密钥。
Pydantic 用于参数验证和配置，LangChain 负责智能体与工具调用。

## 开发与验证

启动及环境配置见 README。依赖安装后提交生成的 `uv.lock`，以便固定依赖版本。
使用真实 MySQL 测试；测试库通过 `TEST_DATABASE_URL` 显式指定，名称以 `_test` 结尾。
测试会清空测试库中的 `items` 表，应为其分配独立账号及权限。

```bash
uv run ruff check backend tests
TEST_DATABASE_URL='mysql+pymysql://user:password@127.0.0.1:3306/taskflow_test?charset=utf8mb4' uv run pytest
```

CI 自动启动 MySQL 8.4 并执行测试。数据库连接、HTTP 请求和模型调用分别需要在
对应服务可用时完成验证；静态检查不能替代端到端验证。
