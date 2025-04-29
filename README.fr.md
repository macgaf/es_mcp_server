# Serveur MCP Elasticsearch

Un serveur d'outils Elasticsearch basé sur le [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk), fournissant des fonctions de requête d'index, de récupération de mapping, de recherche et autres.

Autres langues : [🇨🇳 中文](./README.md) | [🇺🇸 English](./README.en.md) | [🇩🇪 Deutsch](./README.de.md) | [🇯🇵 日本語](./README.jp.md)

## Structure du Projet

```
.
├── es_mcp_server/         # Code du serveur
│   ├── __init__.py        # Initialisation du package
│   ├── server.py          # Programme principal du serveur
│   ├── config.py          # Gestion de la configuration
│   ├── client.py          # Fabrique de client ES
│   └── tools.py           # Implémentation des outils ES MCP
├── es_mcp_client/         # Code du client
│   ├── __init__.py        # Initialisation du package
│   └── client.py          # Programme de test client
├── test/                  # Tests unitaires
│   ├── __init__.py        # Initialisation du package de test
│   └── test_server.py     # Tests unitaires du serveur
├── claude_config_examples/ # Exemples de configuration Claude
│   ├── elasticsearch_stdio_config.json # Configuration en mode stdio
│   └── elasticsearch_sse_config.json   # Configuration en mode sse
├── .vscode/               # Configuration VSCode
│   └── launch.json        # Configuration de débogage
├── docs/                  # Documentation
│   └── requires.md        # Document des exigences
├── pyproject.toml         # Fichier de configuration du projet
├── README.md              # Documentation en chinois
├── README.en.md           # Documentation en anglais
├── README.fr.md           # Documentation en français
├── README.de.md           # Documentation en allemand
├── README.jp.md           # Documentation en japonais
├── .gitignore             # Fichier d'exclusion Git
└── LICENSE                # Licence MIT
```

## Fonctionnalités et Utilisation du Serveur

Le serveur MCP Elasticsearch fournit les outils suivants :

1. **list_indices** - Afficher tous les index du cluster ES
2. **get_mappings** - Renvoyer les informations de mapping des champs pour un index spécifié
3. **search** - Exécuter des requêtes de recherche dans des index spécifiés avec prise en charge de la mise en évidence
4. **get_cluster_health** - Obtenir des informations sur l'état de santé du cluster ES
5. **get_cluster_stats** - Obtenir des informations statistiques d'exécution pour le cluster ES

### Installation

```bash
# Installation depuis PyPI
pip install es-mcp-server

# Ou installation depuis la source
pip install .

# Installation des dépendances de développement
pip install ".[dev]"
```

### Configuration

Le serveur est configuré via des variables d'environnement ou des paramètres de ligne de commande :

| Variable d'Environnement | Description | Valeur par Défaut |
|----------|------|--------|
| ES_HOST | Adresse de l'hôte ES | localhost |
| ES_PORT | Port ES | 9200 |
| ES_USERNAME | Nom d'utilisateur ES | Aucun |
| ES_PASSWORD | Mot de passe ES | Aucun |
| ES_API_KEY | Clé API ES | Aucun |
| ES_USE_SSL | Utilisation de SSL | false |
| ES_VERIFY_CERTS | Vérification des certificats | true |
| ES_VERSION | Version ES (7 ou 8) | 8 |

### Démarrage du Serveur

#### Mode stdio (intégration avec Claude Desktop et autres clients)

```bash
# Utiliser la configuration par défaut
uvx es-mcp-server

# Connexion ES personnalisée
uvx es-mcp-server --host 192.168.0.13 --port 9200 --es-version 8
```

#### Mode SSE (Mode serveur Web)

```bash
# Démarrer le serveur SSE
uvx es-mcp-server --transport sse --host 192.168.0.13 --port 9200
```

## Utilisation du Client

Le projet inclut un programme client pour valider la fonctionnalité du serveur.

### Démarrage du Client

```bash
# Connexion au serveur SSE par défaut (http://localhost:8000/sse)
uvx es-mcp-client

# Adresse de serveur SSE personnalisée
uvx es-mcp-client --url http://example.com:8000/sse
```

## Intégration avec d'Autres Outils

### Intégration avec Claude Desktop

Claude Desktop peut utiliser ce service via le protocole MCP pour accéder aux données Elasticsearch.

#### Configuration en mode stdio

Ajoutez la configuration suivante à Claude Desktop :

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

#### Configuration en mode SSE

Si vous avez déjà démarré un serveur en mode SSE, vous pouvez utiliser la configuration suivante :

```json
{
  "mcpServers": {
    "elasticsearch-mcp-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Tests Unitaires

Exécutez les tests unitaires pour vérifier la fonctionnalité :

```bash
pytest
```

## Développement et Débogage

Ce projet inclut des configurations de débogage VSCode. Après avoir ouvert VSCode, vous pouvez utiliser la fonction de débogage pour démarrer directement le serveur ou le client.

## Remarques

- Ce projet prend en charge les API des versions 7 et 8 d'Elasticsearch
- Le serveur utilise le mode de transport stdio par défaut, adapté à l'intégration avec Claude Desktop et d'autres clients
- Le mode SSE convient au lancement en tant que service autonome

## Licence

[Licence MIT](./LICENSE)

---

*La majorité du code, de la documentation et des exemples de configuration de ce projet ont été générés par claude-3.7-sonnet de cursor, basé sur le [document des exigences](/docs/requires.md) (prompt : générer tous les programmes du projet basés sur ce fichier).* 