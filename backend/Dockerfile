# Python 3.12 ベースイメージ
FROM python:3.12-slim as base

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージ更新とビルド用パッケージインストール
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係ファイルをコピー
COPY requirements.txt .

# Python依存関係をインストール
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 開発環境用ステージ
FROM base as development

# 開発用追加パッケージ
# hadolint ignore=DL3013
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    aiosqlite

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
