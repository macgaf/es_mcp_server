# Elasticsearch MCP Server

An Elasticsearch tool server based on [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk), providing index querying, mapping retrieval, search and other functions.

Other languages: [🇨🇳 中文](./README.md) | [🇫🇷 Français](./README.fr.md) | [🇩🇪 Deutsch](./README.de.md) | [🇯🇵 日本語](./README.jp.md)

## Project Structure

```
.
├── es_mcp_server/         # Server code
│   ├── __init__.py        # Package initialization
│   ├── server.py          # Server main program
│   ├── config.py          # Configuration management
│   ├── client.py          # ES client factory
│   └── tools.py           # ES MCP tool implementation
├── es_mcp_client/         # Client code
│   ├── __init__.py        # Package initialization
│   └── client.py          # Client test program
├── test/                  # Unit tests
│   ├── __init__.py        # Test package initialization
│   └── test_server.py     # Server unit tests
├── claude_config_examples/ # Claude configuration examples
│   ├── elasticsearch_stdio_config.json # stdio mode configuration
│   └── elasticsearch_sse_config.json   # sse mode configuration
├── .vscode/               # VSCode configuration
│   └── launch.json        # Debug configuration
├── docs/                  # Documentation
│   └── requires.md        # Requirements document
├── pyproject.toml         # Project configuration file
├── README.md              # Chinese documentation
├── README.en.md           # English documentation
├── README.fr.md           # French documentation
├── README.de.md           # German documentation
├── README.jp.md           # Japanese documentation
├── .gitignore             # Git ignore file
└── LICENSE                # MIT license
```

## Server Features and Usage

The Elasticsearch MCP server provides the following tools:

1. **list_indices** - Display all indices in the ES cluster
2. **get_mappings** - Return field mapping information for a specified index
3. **search** - Execute search queries in specified indices with highlighting support
4. **get_cluster_health** - Get health status information for the ES cluster
5. **get_cluster_stats** - Get runtime statistical information for the ES cluster

### Installation

```bash
# Install from PyPI
pip install es-mcp-server

# Or install from source
pip install .

# Install development dependencies
pip install ".[dev]"
```

### Configuration

The server is configured via environment variables or command line parameters:

| Environment Variable | Description | Default Value |
|----------|------|--------|
| ES_HOST | ES host address | localhost |
| ES_PORT | ES port | 9200 |
| ES_USERNAME | ES username | None |
| ES_PASSWORD | ES password | None |
| ES_API_KEY | ES API key | None |
| ES_USE_SSL | Whether to use SSL | false |
| ES_VERIFY_CERTS | Whether to verify certificates | true |
| ES_VERSION | ES version (7 or 8) | 8 |

### Starting the Server

#### stdio mode (integration with Claude Desktop and other clients)

```bash
# Use default configuration
uvx es-mcp-server

# Custom ES connection
uvx es-mcp-server --host 192.168.0.13 --port 9200 --es-version 8
```

#### SSE mode (Web server mode)

```bash
# Start the SSE server
uvx es-mcp-server --transport sse --host 192.168.0.13 --port 9200
```

## Client Usage

The project includes a client program for validating server functionality.

### Starting the Client

```bash
# Connect to the default SSE server (http://localhost:8000/sse)
uvx es-mcp-client

# Custom SSE server address
uvx es-mcp-client --url http://example.com:8000/sse
```

## Integration with Other Tools

### Claude Desktop Integration

Claude Desktop can use this service via the MCP protocol to access Elasticsearch data.

#### stdio mode configuration

Add the following configuration to Claude Desktop:

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

#### SSE mode configuration

If you have already started a server in SSE mode, you can use the following configuration:

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Unit Tests

Run unit tests to verify functionality:

```bash
pytest
```

## Development and Debugging

This project includes VSCode debug configurations. After opening VSCode, you can use the debug feature to start the server or client directly.

## Notes

- This project supports both Elasticsearch 7 and 8 version APIs
- The server uses stdio transport mode by default, suitable for integration with Claude Desktop and other clients
- SSE mode is suitable for launching as a standalone service

## License

[MIT License](./LICENSE)

---

*Most of the code, documentation, and configuration examples in this project were generated by cursor's claude-3.7-sonnet based on the [requirements document](/docs/requires.md) (prompt: generate all project programs based on this file).* 