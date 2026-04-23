# mapfan-agent ローカルデモ手順書（分割アーキテクチャ版）

- **日付:** 2026-04-24
- **対象:** 開発チーム向けローカル動作確認デモ
- **実施者:** デモ操作は1名（画面共有想定）
- **所要時間:** 約15〜20分
- **アーキテクチャ:** CLI（OSS）→ HTTP API → Agent Server（非公開）→ MCP Server

## 前提条件

| 項目 | 要件 |
|------|------|
| OS | macOS |
| Python | 3.11以上 |
| uv | インストール済み（`brew install uv` または `curl -LsSf https://astral.sh/uv/install.sh \| sh`） |
| Git | インストール済み |
| ANTHROPIC_API_KEY | デモ実施者が所持 |
| MAPFAN_ACCESS_KEY | デモ実施者が所持（MapFan API用） |

## アーキテクチャ概要

```
ターミナル1              ターミナル2                    ターミナル3
┌────────────────┐     ┌─────────────────────────┐   ┌────────────────────┐
│ MapFan MCP     │     │ mapfan-agent-server     │   │ mapfan-agent CLI   │
│ Server         │◀────│ (Agent + HTTP API)       │◀──│ (OSS CLIツール)     │
│ :8888          │     │ :8000                   │   │                    │
└────────────────┘     └─────────────────────────┘   └────────────────────┘
```

---

## 1. セットアップ（約5分）

### 1.1 ターミナル1: MapFan MCPサーバーの起動

```bash
cd /Users/otsuka/ws/projects/gln/gt-agent/GeoTechAgent-mapfanmcp

# 依存パッケージのインストール（初回のみ）
pip install -r requirements.txt

# 環境変数を設定してHTTPモードで起動
export MAPFAN_ACCESS_KEY="<your-mapfan-access-key>"
export MCP_TRANSPORT="streamable-http"
export MCP_PORT=8888

python main.py
```

起動確認：`Starting streamable-http server on 127.0.0.1:8888` と表示されればOK。

> **このターミナルは開いたままにしてください。**

### 1.2 ターミナル2: APIサーバーの起動

```bash
cd /Users/otsuka/ws/projects/gln/gt-agent/mapfan-agent-server

# 依存パッケージのインストール（初回のみ）
uv sync

# 環境変数を設定
export ANTHROPIC_API_KEY="<your-anthropic-api-key>"
export MAPFAN_MCP_URL="http://localhost:8888/mcp"

# APIサーバーを起動
uv run mapfan-agent-server
```

起動確認：`23 tools loaded from MCP servers.` と `Uvicorn running on http://127.0.0.1:8000` が表示されればOK。

> **このターミナルも開いたままにしてください。**

### 1.3 ターミナル3: CLIツールのセットアップ

```bash
cd /Users/otsuka/ws/projects/gln/gt-agent/mapfan-agent

# 依存パッケージのインストール（初回のみ）
uv sync --dev

# APIサーバーの接続先を設定
export MAPFAN_API_URL="http://localhost:8000"
```

### 1.4 動作確認

```bash
# バージョン確認
uv run mapfan-agent --version
# → mapfan-agent 0.2.0

# ヘルプ表示
uv run mapfan-agent --help
# → ask, repl の2コマンドが表示される

# テストスイートの実行
uv run pytest tests/ -v
# → 11 passed と表示される

# APIサーバーのヘルスチェック
curl http://localhost:8000/api/v1/health
# → {"status":"ok","tools_count":23}
```

---

## 2. デモシナリオ（約10分）

### 2.1 Single-shot モード: 住所検索

```bash
uv run mapfan-agent ask "東京タワーの住所と座標を教えてください"
```

**期待結果:** CLIがHTTP API経由でリクエストを送信し、エージェントがMCPサーバーの住所検索ツールを呼び出し、東京タワーの住所（東京都港区芝公園）と座標を返答する。

### 2.2 Single-shot モード: 周辺スポット検索

```bash
uv run mapfan-agent ask "東京駅周辺のカフェを3件教えてください"
```

**期待結果:** エージェントが住所検索→周辺スポット検索の2ステップで処理し、カフェの名前・距離を含む結果を返す。

### 2.3 Single-shot モード: ルート検索

```bash
uv run mapfan-agent ask "東京駅から東京タワーまでの徒歩ルートを教えてください"
```

**期待結果:** エージェントが2地点の座標を取得後、ルート計算を行い、距離と所要時間を返答する。

### 2.4 REPL モード: 対話型セッション

```bash
uv run mapfan-agent repl
```

REPLが起動したら、以下の会話を順に入力します：

```
> 渋谷駅の座標を教えてください
（結果を確認）

> その周辺500m以内のレストランを探してください
（前の会話コンテキストを活かして検索する — SSEストリーミングで逐次表示）

> exit
```

**期待結果:** 2つ目のクエリで「渋谷駅」の座標を再度聞かなくても、サーバー側のcheckpointerが会話コンテキストを保持しているため、前回取得した座標を利用して周辺検索を行う。

### 2.5 HTTP API 直接アクセス: curl での確認

```bash
# ヘルスチェック
curl http://localhost:8000/api/v1/health
# → {"status":"ok","tools_count":23}

# チャットAPI（プロンプト送信）
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "東京タワーの住所を教えてください"}'
# → {"response":"...","task_id":"...","origin":"human"}

# タスク一覧の確認
curl http://localhost:8000/api/v1/tasks
# → タスクのリストが返る
```

**期待結果:** curlでHTTP API直接アクセスが可能。Web UIからの接続にも同じAPIが使える。

---

## 3. トラブルシューティング

### CLIからAPIサーバーに接続できない

```
Error: Cannot connect to API server at http://localhost:8000
```

- ターミナル2でAPIサーバーが起動中か確認
- `curl http://localhost:8000/api/v1/health` でサーバーに到達できるか確認
- `MAPFAN_API_URL` 環境変数が正しく設定されているか確認

### APIサーバーがMCPサーバーに接続できない

APIサーバー起動時にエラーが出る場合：

- ターミナル1でMCPサーバーが起動中か確認
- `MCP_PORT=8888` と `MCP_TRANSPORT=streamable-http` が設定されているか確認
- `MAPFAN_MCP_URL` 環境変数が正しく設定されているか確認

### APIキーのエラー

```
AuthenticationError: ...
```

- ターミナル2で `echo $ANTHROPIC_API_KEY` でキーが設定されているか確認
- キーが `sk-ant-` で始まっているか確認

### APIサーバーのポートが異なる場合

```bash
# CLIのAPI接続先を変更
export MAPFAN_API_URL="http://localhost:3000"
uv run mapfan-agent ask "テストクエリ"

# またはコマンドラインオプションで指定
uv run mapfan-agent ask --api-url http://localhost:3000 "テストクエリ"
```

---

## 4. デモ後のクリーンアップ

```bash
# ターミナル3: CLIは実行ごとに終了するのでクリーンアップ不要
# ターミナル2: APIサーバーを Ctrl+C で停止
# ターミナル1: MCPサーバーを Ctrl+C で停止

# 環境変数のクリア（必要に応じて）
unset ANTHROPIC_API_KEY
unset MAPFAN_ACCESS_KEY
unset MAPFAN_API_URL
```

---

## 補足: アーキテクチャ詳細（説明用）

```
ユーザー
  │  自然言語クエリ
  ▼
mapfan-agent CLI (OSS)          ← pip install mapfan-agent
  │  HTTP/SSE
  ▼
mapfan-agent-server (非公開)     ← クラウドホスト
  │  LangGraph ReAct ループ
  │  (推論 → ツール呼び出し → 応答)
  ▼
GeoTechAgent-mapfanmcp (MCP Server)
  │  JSON-RPC / Streamable HTTP
  ▼
MapFan API (住所検索 / POI検索 / ルート計算)
```

**リポジトリ分割の理由:**
- Agent Core / LLM統合 / MCP接続のロジックは非公開（知的財産の保護）
- CLIツールはOSSとして公開し、開発者が自由に利用・カスタマイズ可能
- HTTP API経由で接続するため、Web UIや他のクライアントからも同じサーバーを利用可能
