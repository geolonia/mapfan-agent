# mapfan-agent

[![Test](https://github.com/geolonia/mapfan-agent/actions/workflows/test.yml/badge.svg)](https://github.com/geolonia/mapfan-agent/actions/workflows/test.yml)

CLI tool for MapFan geospatial AI agent services. Query geocoding, POI search, and routing via natural language.

mapfan-agentは、MapFanの地理空間AIエージェントサービスを利用するためのCLIツールです。

## Install / インストール

```bash
pip install mapfan-agent
```

## Prerequisites / 前提条件

- Python 3.11+
- Access to a mapfan-agent API server (URL and API key provided by your administrator)
- mapfan-agent APIサーバーへのアクセス（管理者からURLとAPIキーを取得してください）

## Quick Start / クイックスタート

```bash
# Configure API connection / API接続の設定
export MAPFAN_API_URL="https://api.example.com"
export MAPFAN_API_KEY="your-api-key"

# Single query / 単発クエリ
mapfan-agent ask "東京タワー周辺のカフェを探して"

# Interactive mode / 対話モード
mapfan-agent repl
```

## Configuration / 設定

Create `~/.mapfan-agent/config.toml`:

設定ファイル `~/.mapfan-agent/config.toml` を作成:

```toml
[api]
url = "https://api.example.com"
key = "your-api-key"
```

Environment variables override config file:

環境変数で設定ファイルを上書き可能:

| Variable | Description |
|----------|-------------|
| `MAPFAN_API_URL` | API server URL / APIサーバーURL |
| `MAPFAN_API_KEY` | API key / APIキー |

## Commands / コマンド

### `ask` — Single query / 単発クエリ

```bash
mapfan-agent ask "東京駅周辺のカフェを3件教えてください"
mapfan-agent ask --api-url http://localhost:8000 "query"
```

### `repl` — Interactive mode / 対話モード

```bash
mapfan-agent repl
```

Supports conversation context — follow-up questions reference previous answers.

会話コンテキストを保持し、前の回答を参照した質問が可能です。

## Development / 開発

```bash
git clone https://github.com/geolonia/mapfan-agent.git
cd mapfan-agent
uv sync --dev
uv run pytest
```

## Repository Remotes / リモートリポジトリ

This repository is mirrored between Geolonia and GeoTechnologies for joint development and hosting.

| Remote | URL | Purpose |
|--------|-----|---------|
| `geolonia` | `git@github.com:geolonia/mapfan-agent.git` | Geolonia-managed development |
| `geotech` | `git@github.com:GeoTechnologies-Inc-DX/mapfan-agent.git` | GeoTechnologies hosting and handoff |

Push shared updates to both remotes when needed:

```bash
git push geolonia main
git push geotech main
```

## License

MIT
