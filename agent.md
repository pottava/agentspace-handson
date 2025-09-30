# Agentspace カスタムエージェントの体験

## 始めましょう

AI エージェントを Agentspace に登録し、利用するまでの流れを体験していきます。

**[開始]** ボタンをクリックして次のステップに進みます。

<walkthrough-tutorial-duration duration="30"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="1"></walkthrough-tutorial-difficulty>

## 1. プロジェクトの設定

ハンズオン実施対象のプロジェクトを選択してください。

<walkthrough-project-setup></walkthrough-project-setup>

## 2. CLI 初期設定 & API 有効化

選択した環境変数と、ハンズオンで利用するリージョンを環境変数として設定しておきます。

```bash
export GOOGLE_CLOUD_PROJECT=<walkthrough-project-id/>
export GOOGLE_CLOUD_LOCATION="us-central1"
```

[gcloud（Google Cloud の CLI ツール)](https://cloud.google.com/sdk/gcloud?hl=ja) のデフォルト プロジェクトを設定します。

```bash
gcloud config set project "${GOOGLE_CLOUD_PROJECT}"
```

[Vertex AI](https://cloud.google.com/vertex-ai?hl=ja) など、関連サービスを有効化し、利用できる状態にしましょう。

<walkthrough-enable-apis apis=
 "generativelanguage.googleapis.com,
  aiplatform.googleapis.com,
  iamcredentials.googleapis.com,
  cloudresourcemanager.googleapis.com">
</walkthrough-enable-apis>

## 3. 認証

みなさんの権限でアプリケーションを動作させられるよう、[デフォルト認証情報（ADC）](https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=ja) を作成します。表示される URL をブラウザの別タブで開き、認証コードをコピー、ターミナルにもどってきてそれを貼り付け、Enter を押してください。

```bash
gcloud auth application-default login --quiet
```

## 4. AI エージェントの確認

四則演算 AI エージェントです。

関数ツールは <walkthrough-editor-select-line filePath="cloudshell_open/agentspace-handson/app/agent.py" startLine="19" endLine="19" startCharacterOffset="4" endCharacterOffset="100">agent.py の 20 行目</walkthrough-editor-select-line> で設定していますが

呼ばれる <walkthrough-editor-open-file filePath="cloudshell_open/agentspace-handson/app/tools/calculator.py">関数そのもの</walkthrough-editor-open-file> はとてもシンプルな実装です。

ADK は関数の引数やコメント情報を整理して LLM に渡し、どの関数をいつ、どんな引数で呼ぶかを考える手助けをしています。ADK は関数の返り値として **辞書型** を[推奨しています](https://google.github.io/adk-docs/tools/function-tools/#return-type)が、例えば<walkthrough-editor-select-line filePath="cloudshell_open/agentspace-handson/app/tools/calculator.py" startLine="20" endLine="20" startCharacterOffset="8" endCharacterOffset="100">ここ</walkthrough-editor-select-line>ではゼロ除算のときに `{"status": "エラー"}` を返し、LLM に処理が失敗したことを伝えています。

## 5. ローカルでの AI エージェント起動

Python の仮想環境を作り

```bash
cp .devcontainer/pyproject.toml .devcontainer/uv.lock .
uv venv
source .venv/bin/activate
uv sync
```

起動してみましょう。

```bash
export GOOGLE_GENAI_USE_VERTEXAI=1
adk web
```

ターミナルに表示される `INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)` の中のリンクをクリックし、Web UI にアクセスしてください。

試しに以下のような質問をしてみましょう。

```txt
9*(1234+678/32) の答えは？
```

正しい答え `11296.6875` になりましたか？

確認ができたらターミナルにもどり、`Ctrl + C` コマンドで起動中の Web サービスを停止しましょう。

## 6. AI エージェントのテスト

ADK における AI エージェントの評価は Trajectory（軌跡）と最終的な出力で行います。それぞれの閾値をテストの設定として <walkthrough-editor-open-file filePath="cloudshell_open/agentspace-handson/app/eval/data/test_config.json">このように</walkthrough-editor-open-file> に定義してみました。

テストを実行してみましょう。

```bash
adk eval app app/eval/data/eval_data1.evalset.json --config_file_path app/eval/data/test_config.json
```

うまくいけば `Tests passed: 1` となります。fail するようであれば `--print_detailed_results` オプションを有効にして再実行すると

```json
{
    "eval_metric_results": [
        {
            "metric_name": "tool_trajectory_avg_score",
            "threshold": 1.0,
            "score": 0.0
        },
        {
            "metric_name": "response_match_score",
            "threshold": 0.9,
            "score": 0.25
        }
    ]
}
```

など具体的な状況が確認できます。

## 7. Agent Engine へのデプロイ（その 1）

Agent Engine に登録する予定の名前と概要を環境変数に設定しておきます。

```bash
export AGENT_ENGINE_DISPLAY_NAME="Calculator"
export AGENT_ENGINE_DESCRIPTION="An agent that performs arithmetic operations"
```

本来 `adk deploy agent_engine` コマンドが手軽なのですが、2025 年 10 月 1 日現在 [こんな不具合](https://github.com/google/adk-python/issues/2995) が起こっているため、代わりに [Agent Starter Pack (ASP)](https://googlecloudplatform.github.io/agent-starter-pack/) を使ってみます。

```bash
uvx agent-starter-pack enhance --adk -d agent_engine
```

いくつか選択を迫られますが、常に最初の選択肢を選んでしまって問題ありません。

- Continue with enhancement? [Y/n]: -> `Y`
- Select agent directory (1): -> `1` (app)
- Enter the number of your CI/CD runner choice (1): -> `1` (Google Cloud Build)
- Enter desired GCP region (Gemini uses global endpoint by default) (us-central1) -> `us-central1` (Iowa)

## 8. Agent Engine へのデプロイ（その 2）

ASP で生成されたコードも依存解決し

```bash
make install
```

2025 年 10 月 1 日現在意図しない挙動があるため、ちょっとしたワークアラウンドを行いつつ Agent Engine に登録します。（5 分程度はかかるので、気分転換してきてください 🏝 ）

```bash
uv pip freeze > .requirements.txt
mv app/agent_engine_app.py ./
uv run agent_engine_app.py --agent-name "${AGENT_ENGINE_DISPLAY_NAME}"
```

デプロイできたことの確認も兼ねて、リソースの名前を取得してみます。

```bash
api_host="https://${GOOGLE_CLOUD_LOCATION}-aiplatform.googleapis.com"
api_endpoint="${api_host}/v1/projects/${GOOGLE_CLOUD_PROJECT}/locations/${GOOGLE_CLOUD_LOCATION}/reasoningEngines"
export AGENT_ENGINE_RESOURCE_NAME=$( curl -sX GET "${api_endpoint}" -H "Authorization: Bearer $(gcloud auth print-access-token)" | jq -r '.reasoningEngines[] | select(.displayName | contains("Calculator")) | .name' )
echo "${AGENT_ENGINE_RESOURCE_NAME}"
```

## 9. Agent Engine へアクセス

実際に対話してみます。`test_user` としてセッションを開始して

```text
session=$( curl -sX POST "${api_endpoint}/"${AGENT_ENGINE_RESOURCE_NAME##*/}":query" -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-Type: application/json" -d '{"class_method": "async_create_session", "input": {"user_id": "test_user"}}' )
session_id=$( echo "${session}" | jq -r ".output.id")
echo "${session}" | jq .
```

そのセッションを利用してエージェントにメッセージを送信してみます。

```text
message_base='{"class_method": "async_stream_query", "input": {"user_id": "test_user", "message": "(1456 - 98 * 12) / 7 = ?"'
response=$( curl -sX POST "${api_endpoint}/"${AGENT_ENGINE_RESOURCE_NAME##*/}":streamQuery?alt=sse" -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-Type: application/json" -d "${message_base}, \"session_id\": \"${session_id}\"}}" )
echo "${response}" | jq -s ".[-1].content.parts"
```

## 10. Agentspace へ登録（その 1）

作ったエージェントは Google Agentspace へ登録し、同僚たちに使ってもらいましょう。一時フォルダを作り、一般の方が作ってくれたツールをダウンロードします。

```bash
mkdir -p tmp && cd $_
git clone https://github.com/VeerMuchandi/agent_registration_tool.git
cd agent_registration_tool
```

[クラウドの管理コンソール](https://console.cloud.google.com/gen-app-builder/engines)で該当の Agentspace アプリを開き、URL から Agentspace の ID とロケーションを確認します。

例えば `https://console.cloud.google.com/gen-app-builder/locations/<location>/engines/<agentspace-id>/as-overview/..` といった URL の中の

`<agentspace-id>` がその ID であり

```bash
agentspace_id=
```

`<location>` がロケーションです。

```bash
agentspace_location="global"
```

## 11. Agentspace へ登録（その 2）

設定ファイルを `config.json` として用意して

```text
cat << EOF > config.json
{
    "project_id": "${GOOGLE_CLOUD_PROJECT}",
    "location": "${GOOGLE_CLOUD_LOCATION}",
    "re_resource_name": "${AGENT_ENGINE_RESOURCE_NAME}",
    "re_resource_id": "${AGENT_ENGINE_RESOURCE_NAME##*/}",
    "re_display_name": "${AGENT_ENGINE_DISPLAY_NAME}",
    "app_id": "${agentspace_id}",
    "agent_id": "calculator-agent",
    "ars_display_name": "${AGENT_ENGINE_DISPLAY_NAME}",
    "description": "${AGENT_ENGINE_DESCRIPTION}",
    "tool_description": "This is an agent that can perform arithmetic operations. Don't answer based on intuition; think carefully about how to use the tool beforehand and make an effort to serve properly.",
    "adk_deployment_id": "${AGENT_ENGINE_RESOURCE_NAME##*/}",
    "auth_id": "",
    "icon_uri": "",
    "api_location": "${agentspace_location}",
    "re_location": "${GOOGLE_CLOUD_LOCATION}"
}
EOF
```

作られたファイルを <walkthrough-editor-open-file filePath="cloudshell_open/agentspace-handson/tmp/agent_registration_tool/config.json">エディタで開いて</walkthrough-editor-open-file> 確認してください。

`auth_id` と `icon_uri` 以外に  
空欄のフィールドはないでしょうか？  
**もし何かかけていたら、どこかの手順が抜けています。**

## 12. Agentspace へ登録（その 3）

準備ができたら登録します。

```bash
python3 as_registry_client.py register_agent
```

以下のようなエラーがでるかもしれません。  
その場合、現在 Agentspace への登録が制限されている可能性があります。また後日試してみてください。

```json
"error": {
    "code": 404,
    "message": "Method not found.",
    "status": "NOT_FOUND"
}
```

## 13. Agentspace での利用

初期セットアップで準備した Agentspace アプリケーションにユーザとしてアクセスします。

左のサイドメニューから `エージェント` 画面に行くと、いま登録したエージェントが表示されているはずです！実際に対話してみてください。

## これで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

これで `カスタムエージェントの体験` ハンズオンは終了です。

お疲れさまでした！
