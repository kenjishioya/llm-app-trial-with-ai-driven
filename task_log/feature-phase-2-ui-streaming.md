# 🎨 Phase 2 フロントエンド開発計画
**ブランチ**: `feature/phase-2-ui-streaming`

## 📋 Phase 2 概要

**目標**: Next.js 14 チャット UI + SSE ストリーミング + 統合テスト

**完了条件**:
- ✅ ブラウザで http://localhost:3000 にアクセス可能
- ✅ チャット質問→リアルタイム応答表示
- ⏸️ **E2E基本テスト緑（保留中）**
- ✅ フロントエンドテスト成功

---

## 🎯 詳細タスク分解

### Phase 2-1A: 環境セットアップ
#### 優先度: 🔴 最高

**Task 2-1A-1: Node.js環境確認**
- [x] Node.js 20+ バージョン確認
- [x] npm/pnpm パッケージマネージャー確認
- **完了条件**: `node --version` で20以上、`npm --version` 成功
- **所要時間**: 5分
- **コミット**: 不要
- **✅ 実行結果**: Node.js v20.19.1, npm v10.8.2 - 要件満たす
- **✅ 完了日時**: 2024-06-09

**Task 2-1A-2: Next.js 14プロジェクト初期化**
- [x] `frontend/` ディレクトリ作成
- [x] `npx create-next-app@latest frontend --typescript --tailwind --eslint --app`
- [x] 初期設定ファイル確認（next.config.js, tsconfig.json, tailwind.config.js）
- **完了条件**: `cd frontend && npm run dev` でlocalhost:3000表示
- **所要時間**: 10分
- **🔄 コミット**: `feat(frontend): initialize Next.js 14 project with TypeScript and Tailwind`
**✅ 実行結果**: Next.js 14.2.29 + React 18.3.1 + TypeScript + Tailwind CSS + App Router 初期化完了
**✅ 完了日時**: 2024-06-09
**🔧 修正**: Next.js 15→14、React 19→18へのダウングレード（docs要件準拠）

**Task 2-1A-3: shadcn/ui セットアップ**
- [x] `npx shadcn-ui@latest init` 実行
- [x] components.json 設定確認
- [x] 基本コンポーネント追加: `npx shadcn-ui@latest add button card input textarea`
- **完了条件**: `src/components/ui/` に button.tsx, card.tsx, input.tsx, textarea.tsx 存在
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): setup shadcn/ui with basic components`
- **✅ 実行結果**: shadcn v2.6.1 + New York style + 4基本コンポーネント追加完了
- **✅ 完了日時**: 2024-06-09

### Phase 2-1B: GraphQL統合基盤
#### 優先度: 🔴 最高

**Task 2-1B-1: GraphQL クライアント依存関係インストール**
- [x] Apollo Client: `npm install @apollo/client graphql`
- [x] GraphQL Code Generator: `npm install -D @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations @graphql-codegen/typescript-react-apollo`
**完了条件**: package.json に上記パッケージ追加
**所要時間**: 5分
**🔄 コミット**: `feat(frontend): add GraphQL client dependencies`
**✅ 実行結果**: Apollo Client 3.13.8、GraphQL 16.11.0、Code Generator 4パッケージ追加完了
**✅ 完了日時**: 2024-06-09

**Task 2-1B-2: GraphQL Code Generator設定**
- [x] `codegen.yml` 作成
- [x] スキーマURL設定: `http://localhost:8000/graphql`
- [x] 生成設定: TypeScript hooks有効
- [x] npm scripts追加: `"codegen": "graphql-codegen"`
**完了条件**: `npm run codegen` でエラーなし、`src/generated/graphql.ts` 生成
**所要時間**: 10分
**🔄 コミット**: `feat(frontend): configure GraphQL Code Generator`
**✅ 実行結果**: codegen.yml設定、withHooks有効、型安全hooks生成準備完了
**✅ 完了日時**: 2024-06-09

**Task 2-1B-3: Apollo Client設定**
- [x] `src/lib/graphql-client.ts` 作成
- [x] HttpLink設定（環境変数NEXT_PUBLIC_GRAPHQL_URL対応）
- [x] InMemoryCache設定
- [x] エラーポリシー設定
**完了条件**: クライアント設定ファイル作成、型エラーなし
**所要時間**: 15分
**🔄 コミット**: `feat(frontend): setup Apollo Client configuration`
**✅ 実行結果**: HttpLink、InMemoryCache、エラーハンドリング、SSR対応設定完了
**✅ 完了日時**: 2024-06-09

### Phase 2-2A: 基本レイアウト構築
#### 優先度: 🔴 最高

**Task 2-2A-1: ルートレイアウト作成**
- [x] `src/app/layout.tsx` 編集
- [x] Apollo Provider追加
- [x] Tailwind CSS基本設定
- [x] フォント設定（Inter）
**完了条件**: レイアウト適用、Apollo Provider動作
**所要時間**: 10分
**🔄 コミット**: `feat(frontend): setup root layout with Apollo Provider`
**✅ 実行結果**: 日本語対応、QRAIブランディング、メタデータ設定、Apollo Client SSR対応完了
**✅ 完了日時**: 2024-06-09

**Task 2-2A-2: Header コンポーネント作成**
- [x] `src/components/layout/Header.tsx` 作成
- [x] ロゴ・タイトル表示
- [x] Tailwind でスタイリング
- [x] レスポンシブ対応
**完了条件**: ヘッダー表示、モバイル対応確認
**所要時間**: 20分
**🔄 コミット**: `feat(frontend): create Header component`
**✅ 実行結果**: QRAIロゴ・ブランディング、レスポンシブデザイン、ナビゲーション完了
**✅ 完了日時**: 2024-06-09

**Task 2-2A-3: チャットページ作成**
- [x] `src/app/chat/page.tsx` 作成
- [x] 基本レイアウト（ヘッダー + チャット画面）
- [x] プレースホルダーコンテンツ
**完了条件**: /chat アクセスでページ表示
**所要時間**: 15分
**🔄 コミット**: `feat(frontend): create basic chat page`
**✅ 実行結果**: Header統合、プレースホルダーチャットUI、サンプルメッセージ表示完了
**✅ 完了日時**: 2024-06-09

### Phase 2-2B: チャットUIコンポーネント
#### 優先度: 🔴 最高

**Task 2-2B-1: MessageBubble コンポーネント**
- [x] `src/components/chat/MessageBubble.tsx` 作成
- [x] ユーザー・AI メッセージの表示分岐
- [x] Tailwind でスタイリング（青/グレー背景）
- [x] citations プロパティ対応
- [x] isStreaming プロパティ対応
- **完了条件**: メッセージ表示、スタイル確認、型安全性
- **所要時間**: 30分
- **🔄 コミット**: `feat(frontend): create MessageBubble component`
- **✅ 実行結果**: ユーザー/AI メッセージ表示分岐、引用リンク対応、ストリーミング中アニメーション完了
- **✅ 完了日時**: 2024-06-10

**Task 2-2B-2: InputForm コンポーネント**
- [x] `src/components/chat/InputForm.tsx` 作成
- [x] textarea + 送信ボタン
- [x] フォームバリデーション
- [x] isLoading 状態対応
- [x] Enter キー送信（Shift+Enterで改行）
- **完了条件**: フォーム動作、バリデーション、UX確認
- **所要時間**: 25分
- **🔄 コミット**: `feat(frontend): create InputForm component`
- **✅ 実行結果**: フォームバリデーション、文字数制限、キーボードショートカット、UX最適化完了
- **✅ 完了日時**: 2024-06-10

**Task 2-2B-3: LoadingSpinner コンポーネント**
- [x] `src/components/chat/LoadingSpinner.tsx` 作成
- [x] CSS アニメーション設定
- [x] test-id 属性追加
- [x] サイズ・色設定可能
- **完了条件**: スピナーアニメーション、test-id存在
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): create LoadingSpinner component`
- **✅ 実行結果**: 回転スピナー、3点スピナー、LoadingMessage、サイズ・色バリエーション完了
- **✅ 完了日時**: 2024-06-10

**Task 2-2B-4: ChatWindow メインコンポーネント**
- [x] `src/components/chat/ChatWindow.tsx` 作成
- [x] メッセージ配列状態管理
- [x] スクロール制御（自動スクロール）
- [x] MessageBubble + InputForm統合
- [x] 基本的なメッセージ送信フロー
- **完了条件**: チャット画面表示、コンポーネント統合、スクロール動作
- **所要時間**: 35分
- **🔄 コミット**: `feat(frontend): create ChatWindow main component`
- **✅ 実行結果**: ステート管理、自動スクロール、デモ応答、エラーハンドリング、チャットページ統合完了
- **✅ 完了日時**: 2024-06-10

### Phase 2-2C: サイドバー実装（UIレイアウト改善）
#### 優先度: 🔴 最高

**Task 2-2C-1: サイドバーコンポーネント作成**
- [x] `src/components/layout/Sidebar.tsx` 作成
- [x] セッション履歴表示
- [x] 新規チャット作成ボタン
- [x] サイドバー開閉状態管理
- [x] QRAIロゴ統合
- **完了条件**: サイドバー表示、セッション履歴表示
- **所要時間**: 30分
- **🔄 コミット**: `feat(frontend): create sidebar component with session history`
- **✅ 実行結果**: セッション履歴表示、新規チャット機能、削除機能、レスポンシブ対応完了
- **✅ 完了日時**: 2024-12-28

**Task 2-2C-2: サイドバートグル機能**
- [x] ハンバーガーメニューアイコン
- [x] サイドバー開閉アニメーション
- [x] レスポンシブ対応（モバイルで自動非表示）
- [x] トグルボタンをサイドバー内に統合
- **完了条件**: スムーズな開閉アニメーション
- **所要時間**: 20分
- **🔄 コミット**: `feat(frontend): add sidebar toggle with animations`
- **✅ 実行結果**: AppLayout統合、スムーズなアニメーション、レスポンシブ対応完了
- **✅ 完了日時**: 2024-12-28

**Task 2-2C-3: レイアウト統合・調整**
- [x] `src/components/layout/AppLayout.tsx` 作成
- [x] `src/app/layout.tsx` にAppLayout統合
- [x] チャット画面のレイアウト調整
- [x] サイドバー開閉時のコンテンツ幅調整
- [x] ホームページ対応
- [x] 初回セッション重複問題修正
- **完了条件**: バランス良いレイアウト、レスポンシブ動作
- **所要時間**: 35分
- **🔄 コミット**: `feat(frontend): integrate sidebar into main layout`
- **✅ 実行結果**: SessionProvider統合、セッション管理機能、完全なレイアウト統合完了
- **✅ 完了日時**: 2024-12-28

### Phase 2-3A: GraphQL統合実装
#### 優先度: 🟡 高

**Task 2-3A-1: GraphQL型定義生成**
- [x] バックエンド起動確認
- [x] `npm run codegen` 実行
- [x] 生成された型確認（AskInput, AskPayload等）
- [x] 型インポート動作確認
- **完了条件**: 型生成成功、TypeScript エラーなし
- **所要時間**: 10分
- **🔄 コミット**: `feat(frontend): generate GraphQL types from backend schema`
- **✅ 実行結果**: GraphQL Code Generator成功、Apollo Client hooks生成、型安全性確保完了
- **✅ 完了日時**: 2024-06-10

**Task 2-3A-2: ask mutation フック作成**
- [x] 生成されたuseMutationフック使用
- [x] エラーハンドリング追加
- [x] レスポンス型安全性確認
- **完了条件**: ask mutation呼び出し成功、型安全
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): implement ask mutation with type safety`
- **✅ 実行結果**: useAskMutation統合、エラーハンドリング、ローディング状態管理完了
- **✅ 完了日時**: 2024-06-10

**Task 2-3A-3: ChatWindow GraphQL統合**
- [x] ask mutation をChatWindowに統合
- [x] 質問送信→レスポンス受信フロー
- [x] エラー状態表示
- [x] ローディング状態管理
- **完了条件**: 実際の質問送信・応答表示動作
- **所要時間**: 25分
- **🔄 コミット**: `feat(frontend): integrate ask mutation into ChatWindow`
- **✅ 実行結果**: GraphQL mutation統合、セッション管理、useChatSessionフック、完全統合完了
- **✅ 完了日時**: 2024-06-10

### Phase 2-3B: SSEストリーミング実装
#### 優先度: 🟡 高

**Task 2-3B-1: useChatStream フック作成**
- [x] `src/hooks/useChatStream.ts` 作成
- [x] EventSource API統合
- [x] SSE接続・切断管理
- [x] メッセージタイプ分岐（connection_init, chunk, complete, error, message）
- **完了条件**: SSE接続フック、型安全、イベント処理
- **所要時間**: 40分
- **🔄 コミット**: `feat(frontend): create useChatStream hook for SSE`
- **✅ 実行結果**: EventSource API統合、StreamMessage型定義、メッセージ処理ロジック完了
- **✅ 完了日時**: 2024-06-10

**Task 2-3B-2: ストリーミング表示機能**
- [x] チャンク受信→段階的テキスト表示
- [x] メッセージ更新ロジック
- [x] ストリーミング中状態表示
- [x] 完了時の最終化処理
- **完了条件**: リアルタイムテキスト表示、段階的更新
- **所要時間**: 30分
- **🔄 コミット**: `feat(frontend): implement streaming text display`
- **✅ 実行結果**: チャンク処理、段階的テキスト更新、ストリーミング状態管理完了
- **✅ 完了日時**: 2024-06-10

**Task 2-3B-3: エラーハンドリング・再接続**
- [x] SSE接続エラー処理
- [x] 自動再接続ロジック
- [x] タイムアウト処理
- [x] ユーザー向けエラーメッセージ
- **完了条件**: エラー処理動作、再接続機能
- **所要時間**: 25分
- **🔄 コミット**: `feat(frontend): add SSE error handling and reconnection`
- **✅ 実行結果**: エラーハンドリング、バックエンド統合、OpenRouter連携、完全動作確認完了
- **✅ 完了日時**: 2024-06-10

### Phase 2-4A: フロントエンドテスト実装
#### 優先度: 🟢 中

**Task 2-4A-1: Vitest セットアップ**
- [x] `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`
- [x] `vitest.config.ts` 作成
- [x] テスト用setupファイル作成
- [x] package.json scripts追加
- **完了条件**: `npm test` でVitest実行成功
- **所要時間**: 15分
- **🔄 コミット**: `test(frontend): setup Vitest with React Testing Library`
- **✅ 実行結果**: Vitest設定、React Testing Library統合、jsdom環境、テストスクリプト完了
- **✅ 完了日時**: 2024-12-28

**Task 2-4A-2: コンポーネントユニットテスト**
- [x] `frontend/tests/components/MessageBubble.test.tsx` 作成
- [x] `frontend/tests/components/InputForm.test.tsx` 作成
- [x] `frontend/tests/components/LoadingSpinner.test.tsx` 作成
- [x] 各コンポーネントの基本動作テスト
- **完了条件**: 全コンポーネントテスト成功、カバレッジ>80%
- **所要時間**: 45分
- **🔄 コミット**: `test(frontend): add unit tests for chat components`
- **✅ 実行結果**: 30テストケース全成功、高カバレッジ達成、包括的テスト実装完了
- **✅ 完了日時**: 2024-12-28

**Task 2-4A-3: フックユニットテスト**
- [x] `frontend/tests/hooks/useChatSession.test.ts` 作成
- [x] `frontend/tests/hooks/useChatStream.test.ts` 作成
- [x] Apollo Client モック設定
- [x] EventSource モック設定
- [x] ストリーミングロジックテスト
- [x] エラーケーステスト
- **完了条件**: フックテスト成功、エッジケース対応
- **所要時間**: 35分
- **🔄 コミット**: `test(frontend): add unit tests for hooks`
- **✅ 実行結果**: 46テストケース全成功、フック機能完全テスト、EventSourceモック対応完了
- **✅ 完了日時**: 2024-12-28

### Phase 2-4B: E2Eテスト実装 ⏸️ **保留中**
#### 優先度: 🟢 中 → ⏸️ 保留

**Task 2-4B-1: Playwright セットアップ**
- [x] `npm install -D @playwright/test`
- [x] `playwright.config.ts` 作成
- [x] ブラウザ設定（Chromium, Firefox, Safari）
- [x] CI用設定
- **完了条件**: `npx playwright test --ui` でテスト画面表示
- **所要時間**: 20分
- **🔄 コミット**: `test(frontend): setup Playwright for E2E testing`
- **✅ 実行結果**: Playwright設定、複数ブラウザ対応、自動サーバー起動、CI/CD対応設定完了
- **✅ 完了日時**: 2024-12-28

**Task 2-4B-2: 基本チャットフローE2E** ⏸️ **保留中**
- [x] `tests/e2e/basic-chat.spec.ts` 作成
- [x] チャット画面アクセステスト
- [x] メッセージ送信・受信テスト
- [x] ストリーミング表示テスト
- [x] UI要素存在確認テスト
- **完了条件**: E2Eテスト成功、実際のフロー動作確認
- **所要時間**: 40分
- **🔄 コミット**: `test(e2e): add E2E tests for basic chat flow`
- **⏸️ 実行結果**: テスト実装済み、初期エラー修正実施済み、**実行確認は保留中**
- **⏸️ 状況**: 2024-12-28

**Task 2-4B-3: エラーケースE2E** ⏸️ **保留中**
- [x] ネットワークエラーシミュレーション
- [x] SSE接続失敗ケース
- [x] 再接続機能テスト
- [x] バックエンド停止時の動作
- [x] `tests/e2e/error-scenarios.spec.ts` 作成
- **完了条件**: エラーケースE2Eテスト成功
- **所要時間**: 30分
- **🔄 コミット**: `test(e2e): add E2E tests for error scenarios`
- **⏸️ 実行結果**: テスト実装済み、**実行確認は保留中**
- **⏸️ 状況**: 2024-12-28

**⏸️ E2E保留理由**:
- ✅ **実装完了**: Playwright設定、基本フロー・エラーケース両方のテストスペック実装済み
- ✅ **初期修正**: チャット開始フローの修正実施済み
- ⏸️ **実行保留**: 実際のテスト実行・デバッグは後回し
- 🎯 **優先度**: フロントエンド基本機能完成を優先、E2E品質確保は次段階

---

## 🏗️ 修正されたディレクトリ構造

```
llm-app-trial-with-ai-driven/
├── frontend/                    # Next.js フロントエンド
│   ├── src/
│   │   ├── app/                 # Next.js 14 App Router
│   │   │   ├── layout.tsx       # ルートレイアウト
│   │   │   ├── page.tsx         # ホームページ
│   │   │   └── chat/
│   │   │       └── page.tsx     # チャット画面
│   │   ├── components/          # UIコンポーネント
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── InputForm.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   ├── ui/              # shadcn/ui コンポーネント
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── AppLayout.tsx
│   │   │   └── providers/
│   │   │       └── SessionProvider.tsx
│   │   ├── hooks/               # カスタムフック
│   │   │   ├── useChatStream.ts
│   │   │   └── useChatSession.ts
│   │   ├── lib/                 # ユーティリティ・設定
│   │   │   ├── graphql-client.ts
│   │   │   └── utils.ts
│   │   └── generated/           # GraphQL Code Generator出力
│   │       └── graphql.ts
│   ├── tests/                   # ✅ フロントエンドテスト（完了）
│   │   ├── components/          # コンポーネントテスト
│   │   │   ├── MessageBubble.test.tsx
│   │   │   ├── InputForm.test.tsx
│   │   │   └── LoadingSpinner.test.tsx
│   │   ├── hooks/               # フックテスト
│   │   │   ├── useChatStream.test.ts
│   │   │   └── useChatSession.test.ts
│   │   └── setup.ts             # テスト設定
│   ├── public/                  # 静的ファイル
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   └── codegen.yml
├── tests/                       # ⏸️ 統合テスト・E2Eテスト（ルート直下）
│   ├── e2e/                     # ⏸️ E2E テスト（保留中）
│   │   ├── basic-chat.spec.ts   # ⏸️ 実装済み、実行は保留
│   │   ├── error-scenarios.spec.ts # ⏸️ 実装済み、実行は保留
│   │   └── README.md            # ⏸️ E2Eテストドキュメント
│   ├── conftest.py              # 既存：バックエンドテスト設定
│   ├── test_api.py              # 既存：バックエンドAPIテスト
│   └── test_providers.py        # 既存：プロバイダーテスト
├── backend/                     # 既存バックエンド
└── task_log/                    # タスク管理
```

---

## 📊 コミット戦略

### 🔄 安全なコミットタイミング

**頻繁コミット原則**: 各Task完了時に必ずコミット（ファイル削除事故防止）

**コミット形式**:
```
<type>(scope): <description>

feat(frontend): 新機能追加
fix(frontend): バグ修正
test(frontend): テスト追加
refactor(frontend): リファクタリング
docs(frontend): ドキュメント更新
```

**必須コミットポイント**:
1. ✅ **Task 2-1A-2完了時**: Next.js初期化後
2. ✅ **Task 2-1A-3完了時**: shadcn/ui設定後
3. ✅ **Task 2-1B-3完了時**: GraphQL設定完了後
4. ✅ **Task 2-2B-4完了時**: ChatWindow完成後
5. ✅ **Task 2-2C-3完了時**: サイドバー・レイアウト統合完了後
6. ✅ **Task 2-3A-3完了時**: GraphQL統合実装完了後
7. ✅ **Task 2-3B-3完了時**: ストリーミング機能完成後
8. ✅ **Task 2-4A-3完了時**: フロントエンドテスト完成後
9. ⏸️ **Task 2-4B保留**: E2Eテスト実装済み、実行は保留

**🚨 ファイル削除防止策**:
- 各マイルストーン開始前に `git status` 確認
- 新規ファイル作成後、即座にステージング
- Task完了毎のコミットで作業保護
- `git stash` 活用でWIP保存

---

## 📊 品質目標・完了条件

### Phase 2-1 完了条件
- [x] Next.js開発サーバー起動成功
- [x] shadcn/ui コンポーネント使用可能
- [x] GraphQL型生成成功
- [x] Apollo Client接続確認

### Phase 2-2 完了条件
- [x] /chat ページ表示成功
- [x] 全UIコンポーネント表示確認
- [x] レスポンシブ対応確認
- [x] TypeScript エラーゼロ

### 🎯 Phase 2-2B 達成項目
- ✅ **MessageBubble**: ユーザー/AI メッセージ表示、引用リンク、ストリーミングアニメーション
- ✅ **InputForm**: フォームバリデーション、文字数制限、Enter送信、エラーハンドリング
- ✅ **LoadingSpinner**: 回転・3点スピナー、サイズ・色バリエーション、テスト対応
- ✅ **ChatWindow**: メッセージ管理、自動スクロール、デモ応答、全コンポーネント統合
- ✅ **チャットページ統合**: 完全なチャットUI、実際のメッセージ送受信フロー

### 🎯 Phase 2-2C 達成項目
- ✅ **サイドバー**: セッション履歴表示、新規チャット作成、セッション削除機能
- ✅ **レイアウト統合**: AppLayout、SessionProvider、完全なサイドバー統合
- ✅ **レスポンシブ対応**: モバイル・デスクトップ対応、スムーズなアニメーション

### Phase 2-3 完了条件
- [x] GraphQL ask mutation成功
- [x] SSEストリーミング動作確認
- [x] エラーハンドリング動作確認
- [x] フロントエンド・バックエンド統合成功

### 🎯 Phase 2-3A 達成項目
- ✅ **GraphQL型定義生成**: Code Generator + Apollo Client hooks
- ✅ **ask mutation統合**: 型安全なuseAskMutation、エラーハンドリング
- ✅ **セッション管理**: useChatSessionフック、CRUD操作
- ✅ **完全統合**: ChatWindow + GraphQL + セッション管理の完全統合

### 🎯 Phase 2-3B 達成項目
- ✅ **useChatStreamフック**: EventSource API統合、型安全なSSE接続管理
- ✅ **ストリーミング表示**: チャンク受信、段階的テキスト更新、ストリーミング状態表示
- ✅ **エラーハンドリング**: SSE接続エラー処理、自動再接続、タイムアウト処理
- ✅ **バックエンド統合**: OpenRouter連携、リアルタイムチャット完全動作確認

### Phase 2-4 完了条件
- ✅ フロントエンドテストカバレッジ >70%（完了）
- ⏸️ E2Eテスト基本フロー成功（保留中）
- ⏸️ CI/CDパイプライン緑（E2E部分保留）

### 🎯 Phase 2-4A 達成項目（完了）
- ✅ **Vitestセットアップ**: React Testing Library、jsdom環境、テストスクリプト統合
- ✅ **コンポーネントテスト**: MessageBubble、InputForm、LoadingSpinner（30テスト全成功）
- ✅ **フックテスト**: useChatStream、useChatSession（46テスト全成功）
- ✅ **総合テスト品質**: 76テスト全成功、高カバレッジ達成

### ⏸️ Phase 2-4B 保留項目
- ✅ **Playwrightセットアップ**: 複数ブラウザ対応、自動サーバー起動設定済み
- ✅ **E2Eテスト実装**: basic-chat.spec.ts、error-scenarios.spec.ts実装済み
- ⏸️ **実行確認**: 実際のE2Eテスト実行・デバッグは後回し

### 最終完了条件 ✅ **Phase 2基本機能達成**
- ✅ http://localhost:3000/chat で質問送信・AI応答表示
- ✅ ストリーミング応答のリアルタイム表示
- ✅ セッション管理機能（作成・履歴・削除・復元）
- ✅ フロントエンドテスト成功（ユニット・統合）
- ⏸️ E2Eテスト成功（実装済み、実行は保留）
- ✅ パフォーマンス目標達成（初回ロード<2秒）

---

## 🚀 更新されたマイルストーン

### Week 1: 基盤構築 + 基本UI ✅ **完了**
- [x] **ブランチ作成**: `feature/phase-2-ui-streaming`
- [x] **Task 2-1A**: Next.js + shadcn/ui セットアップ（3タスク）
- [x] **Task 2-1B**: GraphQL統合基盤（3タスク）
- [x] **Task 2-2A**: 基本レイアウト（3タスク）
**🎯 Week 1完了**: /chat ページ表示 + GraphQL接続

### Week 2: コンポーネント実装 ✅ **完了**
- [x] **Task 2-2B**: チャットUIコンポーネント（4タスク）
- [x] **Task 2-3A**: GraphQL統合実装（3タスク）
- **🎯 Week 2完了**: 静的チャットUI + GraphQL mutation動作

### Week 3: ストリーミング機能 ✅ **完了**
- [x] **Task 2-3B**: SSEストリーミング実装（3タスク）
- [x] 統合テスト・バグ修正
- **🎯 Week 3完了**: リアルタイムチャット機能完成

### Week 4: テスト・仕上げ ✅ **フロントエンドテスト完了、E2E保留**
- [x] **Task 2-2C**: サイドバー・レイアウト統合（3タスク）
- [x] **Task 2-4A**: フロントエンドテスト（3タスク）
- ⏸️ **Task 2-4B**: E2Eテスト（実装済み、実行保留）
- [x] パフォーマンス調整・最終統合テスト
- **🎯 Week 4完了**: Phase 2基本機能完成（E2E除く）

---

**🎯 Phase 2基本機能完了**

**✅ 達成項目**:
- **完全なチャットUI**: Next.js 14 + TypeScript + shadcn/ui
- **リアルタイムストリーミング**: SSE統合、段階的応答表示
- **セッション管理**: サイドバー、履歴表示、CRUD操作
- **GraphQL統合**: 型安全なAPI呼び出し、エラーハンドリング
- **フロントエンドテスト**: 76テスト全成功、高カバレッジ
- **実用的なQRAI**: ブラウザで実際に動作するチャットアプリケーション

**⏸️ 保留項目**:
- **E2Eテスト**: 実装済み、実行・デバッグは次段階で対応

*作成日: 2024-06-09*
*最終更新: 2024-12-28*
