# Python 3.12 ベースイメージ
FROM python:3.12-slim as base

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージ更新とビルド用パッケージインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.10 \
    curl=8.5.0-2* \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係ファイルをコピー
COPY requirements.txt .

# Python依存関係をインストール
RUN pip install --no-cache-dir --upgrade pip==23.3.2 && \
    pip install --no-cache-dir -r requirements.txt

# 開発環境用ステージ
FROM base as development

# 開発用追加パッケージ
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-cov==4.1.0 \
    pytest-asyncio==0.21.1 \
    aiosqlite==0.19.0

# アプリケーションコードをコピー
COPY . .

# ポート公開
EXPOSE 8000

# デフォルトコマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# プロダクション環境用ステージ
FROM base as production

# アプリケーションコードをコピー
COPY . .

# ポート公開
EXPOSE 8000

# プロダクション用コマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
