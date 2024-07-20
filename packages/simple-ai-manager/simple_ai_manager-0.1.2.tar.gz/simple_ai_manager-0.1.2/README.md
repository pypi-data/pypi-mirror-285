# AI Manager

AI Managerは、複数のAIサービス（OpenAI, Google, Anthropicなど）を統一的に利用するためのPythonライブラリです。このライブラリを使用することで、各社のAPIキー管理や入力ルールを簡単に扱うことができます。

## 特徴

- 複数のAIサービスに対応（OpenAI, Google, Anthropic）
- APIキーの管理が容易
- 柔軟なAPI選択とプロンプト処理
- 環境変数による設定管理

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
MAX_TOKENS=100
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
company = 'openai'  # 'google' または 'anthropic' を使用することも可能
model = 'text-davinci-003'  # 例としてOpenAIのモデル名
prompt = 'Hello, how are you?'

# APIを呼び出してレスポンスを取得
try:
    response = ai_manager.call_api(company, model, prompt)
    print(response)
except Exception as e:
    print(f'Error: {e}')
```

### 各社のAIサービス利用例

#### OpenAI

```python
company = 'openai'
model = 'text-davinci-003'
prompt = 'Hello, how are you?'

response = ai_manager.call_api(company, model, prompt)
print(response)
```

#### Google

```python
company = 'google'
model = 'text-bison-001'
prompt = 'Hello, how are you?'

response = ai_manager.call_api(company, model, prompt)
print(response)
```

#### Anthropic

```python
company = 'anthropic'
model = 'claude'
prompt = 'Hello, how are you?'

response = ai_manager.call_api(company, model, prompt)
print(response)
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
        file.write(response['choices'][0]['message']['content'])
    
    print(f'Response saved to {file_path}')
except Exception as e:
    print(f'Error: {e}')
```

## 貢献

バグの報告や機能のリクエストは[GitHub Issues](https://github.com/555happy/AI_Manager/issues)で受け付けています。プルリクエストも歓迎します。

## ライセンス

このプロジェクトはMITライセンスの下で提供されています