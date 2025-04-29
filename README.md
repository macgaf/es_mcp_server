# Elasticsearch MCP 服务器

基于 [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk) 的 Elasticsearch 工具服务器，提供索引查询、映射获取、搜索等功能。

其他语言版本: [🇺🇸 English](./README.en.md) | [🇫🇷 Français](./README.fr.md) | [🇩🇪 Deutsch](./README.de.md) | [🇯🇵 日本語](./README.jp.md)

## 项目目录结构

```
.
├── es_mcp_server/         # 服务器代码
│   ├── __init__.py        # 包初始化
│   ├── server.py          # 服务器主程序
│   ├── config.py          # 配置管理
│   ├── client.py          # ES客户端工厂
│   └── tools.py           # ES MCP工具实现
├── es_mcp_client/         # 客户端代码
│   ├── __init__.py        # 包初始化
│   └── client.py          # 客户端测试程序
├── test/                  # 单元测试
│   ├── __init__.py        # 测试包初始化
│   └── test_server.py     # 服务器单元测试
├── claude_config_examples/ # Claude配置示例
│   ├── elasticsearch_stdio_config.json # stdio模式配置
│   └── elasticsearch_sse_config.json   # sse模式配置
├── .vscode/               # VSCode配置
│   └── launch.json        # 调试配置
├── docs/                  # 文档
│   └── requires.md        # 需求文档
├── pyproject.toml         # 项目配置文件
├── README.md              # 中文说明文档
├── README.en.md           # 英文说明文档
├── README.fr.md           # 法语说明文档
├── README.de.md           # 德语说明文档
├── README.jp.md           # 日语说明文档
├── .gitignore             # Git忽略文件
└── LICENSE                # MIT许可证
```

## 服务器功能和使用说明

Elasticsearch MCP 服务器提供以下工具：

1. **list_indices** - 显示 ES 集群的所有索引
2. **get_mappings** - 返回指定索引的字段映射信息
3. **search** - 在指定索引中执行搜索查询，支持高亮显示
4. **get_cluster_health** - 获取 ES 集群的健康状态信息
5. **get_cluster_stats** - 获取 ES 集群的运行状态统计信息

### 安装

```bash
# 从PyPI安装
pip install es-mcp-server

# 或从源码安装
pip install .

# 安装开发依赖
pip install ".[dev]"
```

### 配置 

服务器通过环境变量或命令行参数进行配置：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| ES_HOST | ES 主机地址 | localhost |
| ES_PORT | ES 端口 | 9200 |
| ES_USERNAME | ES 用户名 | 无 |
| ES_PASSWORD | ES 密码 | 无 |
| ES_API_KEY | ES API 密钥 | 无 |
| ES_USE_SSL | 是否使用 SSL | false |
| ES_VERIFY_CERTS | 是否验证证书 | true |
| ES_VERSION | ES 版本 (7 或 8) | 8 |

### 启动服务器

#### stdio 模式 (与 Claude Desktop 等客户端集成)

```bash
# 使用默认配置
uvx es-mcp-server

# 自定义 ES 连接
uvx es-mcp-server --host 192.168.0.13 --port 9200 --es-version 8
```

#### SSE 模式 (Web 服务器模式)

```bash
# 启动 SSE 服务器
uvx es-mcp-server --transport sse --host 192.168.0.13 --port 9200
```

## 客户端使用说明

项目包含一个用于验证服务器功能的客户端程序。

### 启动客户端

```bash
# 连接到默认 SSE 服务器 (http://localhost:8000/sse)
uvx es-mcp-client

# 自定义 SSE 服务器地址
uvx es-mcp-client --url http://example.com:8000/sse
```

## 对接其他工具

### 与 Claude Desktop 集成

Claude Desktop 可以通过 MCP 协议使用本服务，以便访问 Elasticsearch 数据。

#### stdio 模式配置

在 Claude Desktop 中添加以下配置：

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "command": "uvx",
      "args": ["es-mcp-server"],
      "env": {
        "ES_HOST": "your-es-host",
        "ES_PORT": "9200",
        "ES_VERSION": "8"
      }
    }
  }
}
```

#### SSE 模式配置

如果您已经启动了 SSE 模式的服务器，可以使用以下配置：

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 单元测试

运行单元测试以验证功能：

```bash
pytest
```

## 开发调试

本项目包含 VSCode 调试配置，打开 VSCode 后可直接使用调试功能启动服务器或客户端。

## 注意事项

- 本项目同时支持 Elasticsearch 7 和 8 版本的 API
- 服务器默认使用 stdio 传输模式，适合与 Claude Desktop 等客户端集成
- SSE 模式适合作为独立服务启动

## 许可证

[MIT License](./LICENSE)

---

*本项目的大部分代码、文档、配置示例都是用cursor的claude-3.7-sonnet根据[需求文档](/docs/requires.md) 生成出来的（提示词：基于本文件生成项目所有程序）。* 