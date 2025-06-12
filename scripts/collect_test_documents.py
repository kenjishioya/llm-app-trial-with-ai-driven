#!/usr/bin/env python3
"""
テストドキュメント収集スクリプト
軽量なデータセットからRAG用テストドキュメントを収集
"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
import requests
from tqdm import tqdm
import pandas as pd

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestDocumentCollector:
    """テストドキュメント収集クラス"""

    def __init__(self, output_dir: str = "test_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # サブディレクトリ作成
        (self.output_dir / "wikipedia").mkdir(exist_ok=True)
        (self.output_dir / "qa_datasets").mkdir(exist_ok=True)
        (self.output_dir / "technical_docs").mkdir(exist_ok=True)
        (self.output_dir / "sample_pdfs").mkdir(exist_ok=True)

    def collect_wikipedia_passages(self, limit: int = 20) -> None:
        """軽量なWikipediaサンプルデータ作成"""
        logger.info(f"Wikipediaサンプルデータを作成中... (件数: {limit})")

        # 実用的なWikipediaスタイルの文書（AI・技術関連）
        wiki_samples = [
            {
                "id": "wiki_ai_001",
                "title": "人工知能",
                "content": "人工知能（じんこうちのう、英: artificial intelligence、AI）とは、人間の知的能力をコンピュータ上で実現する技術の総称である。機械学習、深層学習、自然言語処理、コンピュータビジョンなどの分野が含まれる。近年では大規模言語モデル（LLM）の発展により、テキスト生成、翻訳、要約などのタスクで人間レベルの性能を達成している。主要な応用分野には、チャットボット、自動翻訳、画像認識、音声認識、推薦システムなどがある。",
                "source": "wikipedia_sample",
                "type": "wikipedia_passage"
            },
            {
                "id": "wiki_ml_002",
                "title": "機械学習",
                "content": "機械学習（きかいがくしゅう、英: machine learning、ML）は、人工知能の一分野で、コンピュータがデータから自動的にパターンを学習する技術である。教師あり学習、教師なし学習、強化学習の3つの主要なアプローチがある。代表的なアルゴリズムには線形回帰、決定木、ランダムフォレスト、サポートベクターマシン、ニューラルネットワークなどがある。近年はディープラーニングの発展により、画像認識、自然言語処理、音声認識などの分野で大幅な性能向上を実現している。",
                "source": "wikipedia_sample",
                "type": "wikipedia_passage"
            },
            {
                "id": "wiki_nlp_003",
                "title": "自然言語処理",
                "content": "自然言語処理（しぜんげんごしょり、英: natural language processing、NLP）は、人間が日常的に使っている自然言語をコンピュータに処理させる技術である。形態素解析、構文解析、意味解析、文書分類、機械翻訳、質問応答システムなどの応用がある。近年はTransformerアーキテクチャを基盤とした大規模言語モデルが主流となっている。BERT、GPT、T5などのモデルが様々なNLPタスクで高い性能を示している。",
                "source": "wikipedia_sample",
                "type": "wikipedia_passage"
            },
            {
                "id": "wiki_cloud_004",
                "title": "クラウドコンピューティング",
                "content": "クラウドコンピューティング（英: cloud computing）は、インターネット経由でコンピューティングリソースを提供するサービスモデルである。IaaS（Infrastructure as a Service）、PaaS（Platform as a Service）、SaaS（Software as a Service）の3つの主要なサービス形態がある。主要なクラウドプロバイダーには、Amazon Web Services（AWS）、Microsoft Azure、Google Cloud Platform（GCP）などがある。スケーラビリティ、コスト効率、可用性の向上が主なメリットとして挙げられる。",
                "source": "wikipedia_sample",
                "type": "wikipedia_passage"
            },
            {
                "id": "wiki_azure_005",
                "title": "Microsoft Azure",
                "content": "Microsoft Azure（マイクロソフト アジュール）は、マイクロソフトが提供するクラウドコンピューティングプラットフォームである。仮想マシン、データベース、AI・機械学習サービス、IoTサービスなど200以上のサービスを提供している。Azure OpenAI Service、Azure AI Search、Azure Cognitive Servicesなど、AI関連サービスが充実している。世界60以上のリージョンでサービスを展開し、企業のデジタルトランスフォーメーションを支援している。",
                "source": "wikipedia_sample",
                "type": "wikipedia_passage"
            }
        ]

        # 必要に応じて件数を調整
        wiki_samples = wiki_samples[:min(limit, len(wiki_samples))]

        # JSON保存
        output_file = self.output_dir / "wikipedia" / "wiki_sample_passages.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(wiki_samples, f, ensure_ascii=False, indent=2)

        # 個別テキストファイル保存
        for doc in tqdm(wiki_samples, desc="Wikipediaファイル作成"):
            text_file = self.output_dir / "wikipedia" / f"{doc['id']}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"# {doc['title']}\n\n{doc['content']}")

        logger.info(f"✅ Wikipediaサンプル {len(wiki_samples)}件を作成完了")

    def collect_squad_dataset(self, limit: int = 30) -> None:
        """軽量なSQuADサンプルデータ作成"""
        logger.info(f"SQuADサンプルデータを作成中... (件数: {limit})")

        # 実用的なQ&Aサンプル（技術・ビジネス関連）
        squad_samples = [
            {
                "id": "squad_tech_001",
                "title": "Azure AI Search",
                "content": "Azure AI Searchは、Microsoftが提供するクラウドベースの検索サービスです。フルテキスト検索、ベクトル検索、ハイブリッド検索をサポートし、大規模なドキュメントコレクションから関連情報を高速に検索できます。インデックス作成、クエリ処理、結果ランキングなどの機能を提供し、検索アプリケーションの構築を支援します。",
                "question": "Azure AI Searchはどのような検索方式をサポートしていますか？",
                "answers": {"text": ["フルテキスト検索、ベクトル検索、ハイブリッド検索"], "answer_start": [50]},
                "source": "squad_sample",
                "type": "qa_context"
            },
            {
                "id": "squad_tech_002",
                "title": "RAG（Retrieval-Augmented Generation）",
                "content": "RAGは検索拡張生成と呼ばれる手法で、大規模言語モデル（LLM）の回答生成時に外部の知識源から関連情報を検索して活用します。これにより、モデルの学習データに含まれていない最新情報や専門知識を回答に反映できます。RAGシステムは、文書の取り込み、ベクトル化、検索、生成の4つのステップで構成されます。",
                "question": "RAGシステムは何つのステップで構成されますか？",
                "answers": {"text": ["4つのステップ"], "answer_start": [120]},
                "source": "squad_sample",
                "type": "qa_context"
            },
            {
                "id": "squad_biz_003",
                "title": "デジタルトランスフォーメーション",
                "content": "デジタルトランスフォーメーション（DX）は、デジタル技術を活用して企業の業務プロセス、組織文化、顧客体験を根本的に変革することです。クラウドコンピューティング、AI、IoT、ビッグデータなどの技術を組み合わせて、新しいビジネスモデルの創出や競争優位性の確立を目指します。",
                "question": "DXで活用される主要な技術にはどのようなものがありますか？",
                "answers": {"text": ["クラウドコンピューティング、AI、IoT、ビッグデータ"], "answer_start": [80]},
                "source": "squad_sample",
                "type": "qa_context"
            }
        ]

        # 必要に応じて件数を調整
        squad_samples = squad_samples[:min(limit, len(squad_samples))]

        # JSON保存
        output_file = self.output_dir / "qa_datasets" / "squad_contexts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(squad_samples, f, ensure_ascii=False, indent=2)

        # コンテキストのみをテキストファイルとして保存
        for doc in tqdm(squad_samples, desc="SQuADファイル作成"):
            text_file = self.output_dir / "qa_datasets" / f"{doc['id']}_context.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"# {doc['title']}\n\n{doc['content']}\n\n")
                f.write(f"## Sample Question\n{doc['question']}")

        logger.info(f"✅ SQuADサンプル {len(squad_samples)}件を作成完了")

    def collect_technical_samples(self) -> None:
        """技術文書サンプル作成"""
        logger.info("技術文書サンプルを作成中...")

        # Azure AI関連技術文書サンプル
        azure_ai_doc = """# Azure AI Services 概要

## Azure OpenAI Service
Azure OpenAI Serviceは、OpenAIの強力な言語モデルをAzureクラウド上で利用できるサービスです。

### 主要機能
- GPT-4, GPT-3.5-turbo モデルの利用
- テキスト生成、要約、翻訳
- コード生成とデバッグ支援
- チャットボット構築

### 料金体系
- トークンベースの従量課金制
- モデルごとに異なる料金設定
- 無料枠: 月額$200相当のクレジット

## Azure AI Search
Azure AI Searchは、フルテキスト検索とベクトル検索を組み合わせたハイブリッド検索サービスです。

### 検索機能
- キーワード検索（BM25アルゴリズム）
- セマンティック検索（ベクトル類似度）
- ファセット検索とフィルタリング
- 自動補完とスペル修正

### インデックス設計
- スキーマ定義（フィールド、データ型）
- アナライザー設定（言語別）
- スコアリングプロファイル
- シノニムマップ

## RAG（Retrieval-Augmented Generation）
RAGは検索拡張生成と呼ばれ、外部知識源を活用してLLMの回答精度を向上させる手法です。

### RAGアーキテクチャ
1. ドキュメント取り込み・チャンク分割
2. ベクトル化・インデックス登録
3. クエリ実行・関連文書検索
4. コンテキスト付きプロンプト生成
5. LLMによる回答生成

### 実装のポイント
- チャンクサイズの最適化（500-1000文字）
- オーバーラップ設定（10-20%）
- 検索精度向上（ハイブリッド検索）
- 引用情報の付与
"""

        # Python開発ガイドサンプル
        python_guide_doc = """# Python開発ベストプラクティス

## コーディング規約

### PEP 8準拠
- インデント: スペース4つ
- 行長: 79文字以内
- 命名規則: snake_case（変数・関数）、PascalCase（クラス）

### 型アノテーション
```python
def calculate_score(items: List[Dict[str, Any]]) -> float:
    total = sum(item.get('score', 0) for item in items)
    return total / len(items) if items else 0.0
```

## テスト戦略

### pytest使用
- テスト関数名: `test_` プレフィックス
- フィクスチャ活用
- パラメータ化テスト
- カバレッジ測定

### テストケース例
```python
import pytest
from myapp.calculator import Calculator

class TestCalculator:
    def test_add_positive_numbers(self):
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5

    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
    ])
    def test_add_various_inputs(self, a, b, expected):
        calc = Calculator()
        assert calc.add(a, b) == expected
```

## 非同期プログラミング

### asyncio基本
- `async def` で非同期関数定義
- `await` で非同期処理待機
- `asyncio.gather()` で並行実行

### FastAPI統合
```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/search")
async def search_documents(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/search?q={query}")
        return response.json()
```

## パフォーマンス最適化

### プロファイリング
- `cProfile` でボトルネック特定
- `memory_profiler` でメモリ使用量監視
- `py-spy` で本番環境プロファイリング

### 最適化手法
- リスト内包表記の活用
- ジェネレータ使用でメモリ効率化
- `functools.lru_cache` でキャッシュ
- データベースクエリ最適化
"""

        # FAQ文書サンプル
        faq_doc = """# よくある質問（FAQ）

## システム利用について

### Q1: ログインできません
**A:** 以下の点を確認してください：
- ユーザー名・パスワードが正しいか
- Caps Lockがオンになっていないか
- ブラウザのCookieが有効か
- ネットワーク接続が安定しているか

### Q2: ファイルアップロードが失敗します
**A:** 以下の制限を確認してください：
- ファイルサイズ: 最大100MB
- 対応形式: PDF, DOCX, TXT, Markdown
- ファイル名: 日本語・特殊文字は避ける
- 同時アップロード: 最大5ファイル

### Q3: 検索結果が表示されません
**A:** 検索のコツ：
- キーワードを2-3語に絞る
- 完全一致ではなく部分一致で検索
- 類義語・関連語も試す
- フィルター条件を緩める

## 技術的な問題

### Q4: APIレスポンスが遅いです
**A:** パフォーマンス改善方法：
- クエリを簡潔にする
- 不要なフィールドを除外
- キャッシュ機能を活用
- 同時リクエスト数を制限

### Q5: エラーコード500が発生します
**A:** サーバーエラーの対処法：
- しばらく時間をおいて再試行
- ブラウザキャッシュをクリア
- 管理者に問い合わせ
- エラーログを確認

### Q6: データが更新されません
**A:** データ同期の確認：
- インデックス更新タイミング（5-10分）
- キャッシュ有効期限
- 権限設定の確認
- 手動更新の実行

## 料金・プランについて

### Q7: 利用料金はいくらですか？
**A:** 料金体系：
- 基本プラン: 月額¥1,000（100クエリ/月）
- スタンダード: 月額¥5,000（1,000クエリ/月）
- プレミアム: 月額¥20,000（無制限）
- 従量課金: ¥10/クエリ

### Q8: 無料トライアルはありますか？
**A:** 無料プラン：
- 期間: 30日間
- クエリ数: 50回/月
- 機能制限: 基本検索のみ
- サポート: メールのみ
"""

        # ドキュメント保存
        docs = [
            ("azure_ai_overview.md", azure_ai_doc),
            ("python_best_practices.md", python_guide_doc),
            ("system_faq.md", faq_doc)
        ]

        for filename, content in tqdm(docs, desc="技術文書作成"):
            file_path = self.output_dir / "technical_docs" / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        logger.info(f"✅ 技術文書サンプル {len(docs)}件を作成完了")

    def download_sample_pdfs(self) -> None:
        """サンプルPDFダウンロード（軽量）"""
        logger.info("サンプルPDFをダウンロード中...")

        # 軽量なサンプルPDFのURL
        pdf_urls = [
            {
                "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                "filename": "w3c_dummy_sample.pdf",
                "description": "W3C テストサンプルPDF（軽量）"
            }
        ]

        for pdf_info in tqdm(pdf_urls, desc="PDFダウンロード"):
            try:
                response = requests.get(pdf_info["url"], timeout=30)
                if response.status_code == 200:
                    file_path = self.output_dir / "sample_pdfs" / pdf_info["filename"]
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"✅ ダウンロード完了: {pdf_info['filename']} ({len(response.content)} bytes)")
                else:
                    logger.warning(f"❌ ダウンロード失敗: {pdf_info['url']} (Status: {response.status_code})")
            except Exception as e:
                logger.error(f"❌ PDFダウンロードエラー {pdf_info['url']}: {e}")

    def create_test_manifest(self) -> None:
        """テストドキュメント一覧作成"""
        logger.info("テストドキュメント一覧を作成中...")

        manifest = {
            "created_at": pd.Timestamp.now().isoformat(),
            "total_documents": 0,
            "categories": {
                "wikipedia": {
                    "description": "Wikipediaサンプルデータ（軽量版）",
                    "source": "generated_samples",
                    "count": 0,
                    "files": []
                },
                "qa_datasets": {
                    "description": "Q&Aサンプルデータ（技術・ビジネス関連）",
                    "source": "generated_samples",
                    "count": 0,
                    "files": []
                },
                "technical_docs": {
                    "description": "技術文書サンプル",
                    "source": "generated",
                    "count": 0,
                    "files": []
                },
                "sample_pdfs": {
                    "description": "サンプルPDFファイル（軽量）",
                    "source": "public_resources",
                    "count": 0,
                    "files": []
                }
            }
        }

        # 各カテゴリのファイル数をカウント
        for category in manifest["categories"]:
            category_path = self.output_dir / category
            if category_path.exists():
                files = list(category_path.glob("*"))
                manifest["categories"][category]["count"] = len(files)
                manifest["categories"][category]["files"] = [f.name for f in files]
                manifest["total_documents"] += len(files)

        # マニフェスト保存
        manifest_file = self.output_dir / "test_documents_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ テストドキュメント一覧作成完了: 合計 {manifest['total_documents']} ファイル")

        # サマリー表示
        print("\n" + "="*60)
        print("📄 テストドキュメント収集完了")
        print("="*60)
        for category, info in manifest["categories"].items():
            print(f"📁 {category}: {info['count']}件 ({info['description']})")
        print(f"📊 合計: {manifest['total_documents']}件")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="RAG用テストドキュメント収集（軽量版）")
    parser.add_argument("--output-dir", default="test_documents", help="出力ディレクトリ")
    parser.add_argument("--wiki-limit", type=int, default=5, help="Wikipedia文書数制限")
    parser.add_argument("--squad-limit", type=int, default=3, help="SQuAD文書数制限")
    parser.add_argument("--skip-download", action="store_true", help="PDFダウンロードをスキップ")
    parser.add_argument("--verbose", action="store_true", help="詳細ログ表示")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    collector = TestDocumentCollector(args.output_dir)

    try:
        print("🚀 テストドキュメント収集を開始...")

        # データ収集実行
        collector.collect_wikipedia_passages(args.wiki_limit)
        collector.collect_squad_dataset(args.squad_limit)
        collector.collect_technical_samples()

        if not args.skip_download:
            collector.download_sample_pdfs()

        # マニフェスト作成
        collector.create_test_manifest()

        print(f"\n✅ テストドキュメント収集完了！")
        print(f"📁 出力先: {args.output_dir}")
        print(f"📋 詳細: {args.output_dir}/test_documents_manifest.json")

    except Exception as e:
        logger.error(f"❌ テストドキュメント収集エラー: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
