# Elasticsearch MCP Server

Ein Elasticsearch-Tool-Server basierend auf dem [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk), der Index-Abfragen, Mapping-Abruf, Suche und andere Funktionen bereitstellt.

Andere Sprachen: [🇨🇳 中文](./README.md) | [🇺🇸 English](./README.en.md) | [🇫🇷 Français](./README.fr.md) | [🇯🇵 日本語](./README.jp.md)

## Projektstruktur

```
.
├── es_mcp_server/         # Server-Code
│   ├── __init__.py        # Paket-Initialisierung
│   ├── server.py          # Server-Hauptprogramm
│   ├── config.py          # Konfigurationsverwaltung
│   ├── client.py          # ES-Client-Factory
│   └── tools.py           # ES MCP-Tool-Implementierung
├── es_mcp_client/         # Client-Code
│   ├── __init__.py        # Paket-Initialisierung
│   └── client.py          # Client-Testprogramm
├── test/                  # Unit-Tests
│   ├── __init__.py        # Test-Paket-Initialisierung
│   └── test_server.py     # Server-Unit-Tests
├── claude_config_examples/ # Claude-Konfigurationsbeispiele
│   ├── elasticsearch_stdio_config.json # stdio-Modus-Konfiguration
│   └── elasticsearch_sse_config.json   # sse-Modus-Konfiguration
├── .vscode/               # VSCode-Konfiguration
│   └── launch.json        # Debug-Konfiguration
├── docs/                  # Dokumentation
│   └── requires.md        # Anforderungsdokument
├── pyproject.toml         # Projektkonfigurationsdatei
├── README.md              # Chinesische Dokumentation
├── README.en.md           # Englische Dokumentation
├── README.fr.md           # Französische Dokumentation
├── README.de.md           # Deutsche Dokumentation
├── README.jp.md           # Japanische Dokumentation
├── .gitignore             # Git-Ignorier-Datei
└── LICENSE                # MIT-Lizenz
```

## Server-Funktionen und Nutzung

Der Elasticsearch MCP-Server bietet folgende Tools:

1. **list_indices** - Alle Indizes im ES-Cluster anzeigen
2. **get_mappings** - Feld-Mapping-Informationen für einen angegebenen Index zurückgeben
3. **search** - Suchanfragen in angegebenen Indizes mit Hervorhebungsunterstützung ausführen
4. **get_cluster_health** - Gesundheitsstatusinformationen für den ES-Cluster abrufen
5. **get_cluster_stats** - Laufzeitstatistikinformationen für den ES-Cluster abrufen

### Installation

```bash
# Von PyPI installieren
pip install es-mcp-server

# Oder aus Quellcode installieren
pip install .

# Entwicklungsabhängigkeiten installieren
pip install ".[dev]"
```

### Konfiguration

Der Server wird über Umgebungsvariablen oder Kommandozeilenparameter konfiguriert:

| Umgebungsvariable | Beschreibung | Standardwert |
|----------|------|--------|
| ES_HOST | ES-Host-Adresse | localhost |
| ES_PORT | ES-Port | 9200 |
| ES_USERNAME | ES-Benutzername | Keiner |
| ES_PASSWORD | ES-Passwort | Keiner |
| ES_API_KEY | ES-API-Schlüssel | Keiner |
| ES_USE_SSL | Ob SSL verwendet werden soll | false |
| ES_VERIFY_CERTS | Ob Zertifikate überprüft werden sollen | true |
| ES_VERSION | ES-Version (7 oder 8) | 8 |

### Server starten

#### stdio-Modus (Integration mit Claude Desktop und anderen Clients)

```bash
# Standardkonfiguration verwenden
uvx es-mcp-server

# Benutzerdefinierte ES-Verbindung
uvx es-mcp-server --host 192.168.0.13 --port 9200 --es-version 8
```

#### SSE-Modus (Webserver-Modus)

```bash
# SSE-Server starten
uvx es-mcp-server --transport sse --host 192.168.0.13 --port 9200
```

## Client-Nutzung

Das Projekt enthält ein Client-Programm zur Validierung der Server-Funktionalität.

### Client starten

```bash
# Mit dem Standard-SSE-Server verbinden (http://localhost:8000/sse)
uvx es-mcp-client

# Benutzerdefinierte SSE-Server-Adresse
uvx es-mcp-client --url http://example.com:8000/sse
```

## Integration mit anderen Tools

### Claude Desktop-Integration

Claude Desktop kann diesen Dienst über das MCP-Protokoll nutzen, um auf Elasticsearch-Daten zuzugreifen.

#### stdio-Modus-Konfiguration

Fügen Sie die folgende Konfiguration zu Claude Desktop hinzu:

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

#### SSE-Modus-Konfiguration

Wenn Sie bereits einen Server im SSE-Modus gestartet haben, können Sie die folgende Konfiguration verwenden:

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Unit-Tests

Führen Sie Unit-Tests aus, um die Funktionalität zu überprüfen:

```bash
pytest
```

## Entwicklung und Debugging

Dieses Projekt enthält VSCode-Debug-Konfigurationen. Nach dem Öffnen von VSCode können Sie die Debug-Funktion verwenden, um den Server oder Client direkt zu starten.

## Hinweise

- Dieses Projekt unterstützt sowohl Elasticsearch 7 als auch 8 Version APIs
- Der Server verwendet standardmäßig den stdio-Transportmodus, der für die Integration mit Claude Desktop und anderen Clients geeignet ist
- Der SSE-Modus eignet sich für den Start als eigenständiger Dienst

## Lizenz

[MIT-Lizenz](./LICENSE)

---

*Der Großteil des Codes, der Dokumentation und der Konfigurationsbeispiele in diesem Projekt wurden von cursor's claude-3.7-sonnet basierend auf dem [Anforderungsdokument](/docs/requires.md) generiert (Prompt: Alle Projektprogramme basierend auf dieser Datei generieren).* 