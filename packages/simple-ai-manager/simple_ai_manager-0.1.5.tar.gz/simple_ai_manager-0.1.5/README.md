# AI Manager

AI Managerは、複数のAIサービス（OpenAI, Google, Anthropicなど）を統一的に利用するためのPythonライブラリです。このライブラリを使用することで、各社のAPIキー管理や入力ルールを簡単に扱うことができます。また、連続した会話の管理機能も提供しています。

## 特徴

- 複数のAIサービスに対応（OpenAI, Google, Anthropic）
- APIキーの管理が容易
- 柔軟なAPI選択とプロンプト処理
- 環境変数による設定管理
- テキストに特化した設計
- 連続した会話の管理機能

## インストール

以下のコマンドを使用して、pip経由でライブラリをインストールします。

```bash
pip install simple-ai-manager
```

## 環境設定

環境変数を使用してAPIキーを管理します。プロジェクトディレクトリに`.env`ファイルを作成し、以下のようにAPIキーを設定してください。

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

トークン数の制限をかけたい場合は、以下のように環境変数にMAX_TOKENSを書いて設定してください。

```env
MAX_TOKENS=10000
```
設定しない場合は、デフォルト値が使われます。
デフォルト値は以下の通りです。
openai/1000
google/8192
anthropic/1000

## 使い方

### 基本的な使い方

AI Managerを使用して、各社のAIサービスを呼び出す基本的な方法を示します。

```python
from dotenv import load_dotenv
import os
from simple_ai_manager import AIManager

# 環境変数の読み込み
load_dotenv()

# AIManagerのインスタンスを作成
ai_manager = AIManager()

# 使用するAIの会社、モデル、プロンプトを設定
company = 'openai'  # 'google' または 'anthropic' も使用可能
model = 'text-davinci-003'  # 例としてOpenAIのモデル名
prompt = 'Hello, how are you?'

# APIを呼び出してレスポンスを取得
try:
    response = ai_manager.call_api(company, model, prompt)
    print(response)
except Exception as e:
    print(f'Error: {e}')
```

レスポンスはテキストだけに限定させています。
テキストを渡してテキストで貰うときに特化した簡略化ツールです。

### 会話の継続性管理

AI Managerは会話の継続性を管理する機能を提供しています。この機能を使用することで、連続した質問や対話を行うことができます。

#### 会話の開始

```python
conversation_id = ai_manager.start_conversation('openai', 'gpt-4', save_conversation=True)
```

#### 会話の継続

```python
response1 = ai_manager.call_api('openai', 'gpt-4', "こんにちは。今日の天気について教えてください。", conversation_id)
print(response1)

response2 = ai_manager.call_api('openai', 'gpt-4', "その天気は週末まで続きますか？", conversation_id)
print(response2)
```

#### 会話の終了

```python
ai_manager.end_conversation(conversation_id)
```

### 会話保存のオンオフ

会話の保存機能は、デフォルトでオフになっています。特定の会話で保存機能をオンにしたい場合は、以下のように`save_conversation`パラメータを`True`に設定します：

```python
conversation_id = ai_manager.start_conversation('openai', 'gpt-4', save_conversation=True)
```

または、AIManagerのインスタンス作成時に全体的な設定を行うこともできます：

```python
ai_manager = AIManager(default_save_conversation=True)
```

この場合、すべての会話で保存機能が有効になります。特定の会話で保存機能を無効にしたい場合は、以下のようにします：

```python
conversation_id = ai_manager.start_conversation('openai', 'gpt-4', save_conversation=False)
```

会話の保存機能を使用しない場合、各`call_api`呼び出しは独立したリクエストとして処理され、前後の文脈は考慮されません。これは、単発の質問や、文脈を必要としないタスクに適しています。

### 保存された会話の取得

保存された会話を取得するには、以下のメソッドを使用します：

```python
conversation_history = ai_manager.get_conversation_history(conversation_id)
```

### AIからの返答をファイルに保存

AIからの返答を指定したディレクトリに`yyyymmddhhmmss.txt`形式で保存する方法を示します。

```python
import datetime

company = 'openai'
model = 'text-davinci-003'
prompt = 'Hello, how are you?'

try:
    response = ai_manager.call_api(company, model, prompt)
    
    # 取得結果（AIからの返事）を保存するディレクトリ
    save_dir = 'ai_responses'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 現在の日時を使用してファイル名を生成
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    file_path = os.path.join(save_dir, f'{timestamp}.txt')
    
    # AIの返答をファイルに保存
    with open(file_path, 'w') as file:
        file.write(response)
    
    print(f'Response saved to {file_path}')
except Exception as e:
    print(f'Error: {e}')
```

## 貢献

バグの報告や機能のリクエストは[GitHub Issues](https://github.com/555happy/AI_Manager/issues)で受け付けています。プルリクエストも歓迎します。

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。