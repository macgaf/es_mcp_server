# Elasticsearch MCP サーバー

[Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk) に基づく Elasticsearch ツールサーバーで、インデックスクエリ、マッピング取得、検索などの機能を提供します。

他の言語: [🇨🇳 中文](./README.md) | [🇺🇸 English](./README.en.md) | [🇫🇷 Français](./README.fr.md) | [🇩🇪 Deutsch](./README.de.md)

## プロジェクト構造

```
.
├── es_mcp_server/         # サーバーコード
│   ├── __init__.py        # パッケージ初期化
│   ├── server.py          # サーバーメインプログラム
│   ├── config.py          # 設定管理
│   ├── client.py          # ES クライアントファクトリ
│   └── tools.py           # ES MCP ツール実装
├── es_mcp_client/         # クライアントコード
│   ├── __init__.py        # パッケージ初期化
│   └── client.py          # クライアントテストプログラム
├── test/                  # ユニットテスト
│   ├── __init__.py        # テストパッケージ初期化
│   └── test_server.py     # サーバーユニットテスト
├── claude_config_examples/ # Claude 設定例
│   ├── elasticsearch_stdio_config.json # stdio モード設定
│   └── elasticsearch_sse_config.json   # sse モード設定
├── .vscode/               # VSCode 設定
│   └── launch.json        # デバッグ設定
├── docs/                  # ドキュメント
│   └── requires.md        # 要件ドキュメント
├── pyproject.toml         # プロジェクト設定ファイル
├── README.md              # 中国語ドキュメント
├── README.en.md           # 英語ドキュメント
├── README.fr.md           # フランス語ドキュメント
├── README.de.md           # ドイツ語ドキュメント
├── README.jp.md           # 日本語ドキュメント
├── .gitignore             # Git 無視ファイル
└── LICENSE                # MIT ライセンス
```

## サーバー機能と使用方法

Elasticsearch MCP サーバーは以下のツールを提供します：

1. **list_indices** - ES クラスターのすべてのインデックスを表示
2. **get_mappings** - 指定されたインデックスのフィールドマッピング情報を返す
3. **search** - 指定されたインデックスで検索クエリを実行し、ハイライト表示をサポート
4. **get_cluster_health** - ES クラスターの健全性状態情報を取得
5. **get_cluster_stats** - ES クラスターのランタイム統計情報を取得

### インストール

```bash
# PyPI からインストール
pip install es-mcp-server

# またはソースからインストール
pip install .

# 開発依存関係をインストール
pip install ".[dev]"
```

### 設定

サーバーは環境変数またはコマンドラインパラメータで設定されます：

| 環境変数 | 説明 | デフォルト値 |
|----------|------|--------|
| ES_HOST | ES ホストアドレス | localhost |
| ES_PORT | ES ポート | 9200 |
| ES_USERNAME | ES ユーザー名 | なし |
| ES_PASSWORD | ES パスワード | なし |
| ES_API_KEY | ES API キー | なし |
| ES_USE_SSL | SSL を使用するかどうか | false |
| ES_VERIFY_CERTS | 証明書を検証するかどうか | true |
| ES_VERSION | ES バージョン (7 または 8) | 8 |

### サーバーの起動

#### stdio モード (Claude Desktop などのクライアントとの統合)

```bash
# デフォルト設定を使用
uvx es-mcp-server

# カスタム ES 接続
uvx es-mcp-server --host 192.168.0.13 --port 9200 --es-version 8
```

#### SSE モード (Web サーバーモード)

```bash
# SSE サーバーを起動
uvx es-mcp-server --transport sse --host 192.168.0.13 --port 9200
```

## クライアント使用方法

プロジェクトにはサーバーの機能を検証するためのクライアントプログラムが含まれています。

### クライアントの起動

```bash
# デフォルトの SSE サーバーに接続 (http://localhost:8000/sse)
uvx es-mcp-client

# カスタム SSE サーバーアドレス
uvx es-mcp-client --url http://example.com:8000/sse
```

## 他のツールとの統合

### Claude Desktop との統合

Claude Desktop は MCP プロトコルを介してこのサービスを使用し、Elasticsearch データにアクセスできます。

#### stdio モード設定

Claude Desktop に以下の設定を追加します：

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

#### SSE モード設定

SSE モードでサーバーを既に起動している場合は、以下の設定を使用できます：

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## ユニットテスト

機能を検証するためにユニットテストを実行します：

```bash
pytest
```

## 開発とデバッグ

このプロジェクトには VSCode デバッグ設定が含まれています。VSCode を開いた後、デバッグ機能を使用してサーバーまたはクライアントを直接起動できます。

## 注意事項

- このプロジェクトは Elasticsearch 7 と 8 の両方のバージョン API をサポートしています
- サーバーはデフォルトで stdio 転送モードを使用し、Claude Desktop などのクライアントとの統合に適しています
- SSE モードはスタンドアロンサービスとして起動するのに適しています

## ライセンス

[MIT ライセンス](./LICENSE)

---

*このプロジェクトの大部分のコード、ドキュメント、設定例は、[要件ドキュメント](/docs/requires.md)に基づいて cursor の claude-3.7-sonnet によって生成されました（プロンプト：このファイルに基づいてプロジェクトのすべてのプログラムを生成する）。* 