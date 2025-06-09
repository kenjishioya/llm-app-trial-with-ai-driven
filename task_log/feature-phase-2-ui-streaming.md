# 🎨 Phase 2 フロントエンド開発計画
**ブランチ**: `feature/phase-2-ui-streaming`

## 📋 Phase 2 概要

**目標**: Next.js 14 チャット UI + SSE ストリーミング + 統合テスト

**完了条件**:
- ✅ ブラウザで http://localhost:3000 にアクセス可能
- ✅ チャット質問→リアルタイム応答表示
- ✅ E2E基本テスト緑
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
- **✅ 実行結果**: Next.js 15.3.3 + React 19 + TypeScript + Tailwind CSS + App Router 初期化完了
- **✅ 完了日時**: 2024-06-09

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
- [ ] Apollo Client: `npm install @apollo/client graphql`
- [ ] GraphQL Code Generator: `npm install -D @graphql-codegen/cli @graphql-codegen/typescript @graphql-codegen/typescript-operations @graphql-codegen/typescript-react-apollo`
- **完了条件**: package.json に上記パッケージ追加
- **所要時間**: 5分
- **🔄 コミット**: `feat(frontend): add GraphQL client dependencies`

**Task 2-1B-2: GraphQL Code Generator設定**
- [ ] `codegen.yml` 作成
- [ ] スキーマURL設定: `http://localhost:8000/graphql`
- [ ] 生成設定: TypeScript hooks有効
- [ ] npm scripts追加: `"codegen": "graphql-codegen"`
- **完了条件**: `npm run codegen` でエラーなし、`src/generated/graphql.ts` 生成
- **所要時間**: 10分
- **🔄 コミット**: `feat(frontend): configure GraphQL Code Generator`

**Task 2-1B-3: Apollo Client設定**
- [ ] `src/lib/graphql-client.ts` 作成
- [ ] HttpLink設定（環境変数NEXT_PUBLIC_GRAPHQL_URL対応）
- [ ] InMemoryCache設定
- [ ] エラーポリシー設定
- **完了条件**: クライアント設定ファイル作成、型エラーなし
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): setup Apollo Client configuration`

### Phase 2-2A: 基本レイアウト構築
#### 優先度: 🔴 最高

**Task 2-2A-1: ルートレイアウト作成**
- [ ] `src/app/layout.tsx` 編集
- [ ] Apollo Provider追加
- [ ] Tailwind CSS基本設定
- [ ] フォント設定（Inter）
- **完了条件**: レイアウト適用、Apollo Provider動作
- **所要時間**: 10分
- **🔄 コミット**: `feat(frontend): setup root layout with Apollo Provider`

**Task 2-2A-2: Header コンポーネント作成**
- [ ] `src/components/layout/Header.tsx` 作成
- [ ] ロゴ・タイトル表示
- [ ] Tailwind でスタイリング
- [ ] レスポンシブ対応
- **完了条件**: ヘッダー表示、モバイル対応確認
- **所要時間**: 20分
- **🔄 コミット**: `feat(frontend): create Header component`

**Task 2-2A-3: チャットページ作成**
- [ ] `src/app/chat/page.tsx` 作成
- [ ] 基本レイアウト（ヘッダー + チャット画面）
- [ ] プレースホルダーコンテンツ
- **完了条件**: /chat アクセスでページ表示
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): create basic chat page`

### Phase 2-2B: チャットUIコンポーネント
#### 優先度: 🔴 最高

**Task 2-2B-1: MessageBubble コンポーネント**
- [ ] `src/components/chat/MessageBubble.tsx` 作成
- [ ] ユーザー・AI メッセージの表示分岐
- [ ] Tailwind でスタイリング（青/グレー背景）
- [ ] citations プロパティ対応
- [ ] isStreaming プロパティ対応
- **完了条件**: メッセージ表示、スタイル確認、型安全性
- **所要時間**: 30分
- **🔄 コミット**: `feat(frontend): create MessageBubble component`

**Task 2-2B-2: InputForm コンポーネント**
- [ ] `src/components/chat/InputForm.tsx` 作成
- [ ] textarea + 送信ボタン
- [ ] フォームバリデーション
- [ ] isLoading 状態対応
- [ ] Enter キー送信（Shift+Enterで改行）
- **完了条件**: フォーム動作、バリデーション、UX確認
- **所要時間**: 25分
- **🔄 コミット**: `feat(frontend): create InputForm component`

**Task 2-2B-3: LoadingSpinner コンポーネント**
- [ ] `src/components/chat/LoadingSpinner.tsx` 作成
- [ ] CSS アニメーション設定
- [ ] test-id 属性追加
- [ ] サイズ・色設定可能
- **完了条件**: スピナーアニメーション、test-id存在
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): create LoadingSpinner component`

**Task 2-2B-4: ChatWindow メインコンポーネント**
- [ ] `src/components/chat/ChatWindow.tsx` 作成
- [ ] メッセージ配列状態管理
- [ ] スクロール制御（自動スクロール）
- [ ] MessageBubble + InputForm統合
- [ ] 基本的なメッセージ送信フロー
- **完了条件**: チャット画面表示、コンポーネント統合、スクロール動作
- **所要時間**: 35分
- **🔄 コミット**: `feat(frontend): create ChatWindow main component`

### Phase 2-3A: GraphQL統合実装
#### 優先度: 🟡 高

**Task 2-3A-1: GraphQL型定義生成**
- [ ] バックエンド起動確認
- [ ] `npm run codegen` 実行
- [ ] 生成された型確認（AskInput, AskPayload等）
- [ ] 型インポート動作確認
- **完了条件**: 型生成成功、TypeScript エラーなし
- **所要時間**: 10分
- **🔄 コミット**: `feat(frontend): generate GraphQL types from backend schema`

**Task 2-3A-2: ask mutation フック作成**
- [ ] 生成されたuseMutationフック使用
- [ ] エラーハンドリング追加
- [ ] レスポンス型安全性確認
- **完了条件**: ask mutation呼び出し成功、型安全
- **所要時間**: 15分
- **🔄 コミット**: `feat(frontend): implement ask mutation with type safety`

**Task 2-3A-3: ChatWindow GraphQL統合**
- [ ] ask mutation をChatWindowに統合
- [ ] 質問送信→レスポンス受信フロー
- [ ] エラー状態表示
- [ ] ローディング状態管理
- **完了条件**: 実際の質問送信・応答表示動作
- **所要時間**: 25分
- **🔄 コミット**: `feat(frontend): integrate ask mutation into ChatWindow`

### Phase 2-3B: SSEストリーミング実装
#### 優先度: 🟡 高

**Task 2-3B-1: useChatStream フック作成**
- [ ] `src/hooks/useChatStream.ts` 作成
- [ ] EventSource API統合
- [ ] SSE接続・切断管理
- [ ] メッセージタイプ分岐（connection_init, chunk, complete, error）
- **完了条件**: SSE接続フック、型安全、イベント処理
- **所要時間**: 40分
- **🔄 コミット**: `feat(frontend): create useChatStream hook for SSE`

**Task 2-3B-2: ストリーミング表示機能**
- [ ] チャンク受信→段階的テキスト表示
- [ ] メッセージ更新ロジック
- [ ] ストリーミング中状態表示
- [ ] 完了時の最終化処理
- **完了条件**: リアルタイムテキスト表示、段階的更新
- **所要時間**: 30分
- **🔄 コミット**: `feat(frontend): implement streaming text display`

**Task 2-3B-3: エラーハンドリング・再接続**
- [ ] SSE接続エラー処理
- [ ] 自動再接続ロジック
- [ ] タイムアウト処理
- [ ] ユーザー向けエラーメッセージ
- **完了条件**: エラー処理動作、再接続機能
- **所要時間**: 25分
- **🔄 コミット**: `feat(frontend): add SSE error handling and reconnection`

### Phase 2-4A: テスト実装
#### 優先度: 🟢 中

**Task 2-4A-1: Vitest セットアップ**
- [ ] `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`
- [ ] `vitest.config.ts` 作成
- [ ] テスト用setupファイル作成
- [ ] package.json scripts追加
- **完了条件**: `npm test` でVitest実行成功
- **所要時間**: 15分
- **🔄 コミット**: `test(frontend): setup Vitest with React Testing Library`

**Task 2-4A-2: コンポーネントユニットテスト**
- [ ] `tests/frontend/components/MessageBubble.test.tsx` 作成
- [ ] `tests/frontend/components/InputForm.test.tsx` 作成
- [ ] `tests/frontend/components/LoadingSpinner.test.tsx` 作成
- [ ] 各コンポーネントの基本動作テスト
- **完了条件**: 全コンポーネントテスト成功、カバレッジ>80%
- **所要時間**: 45分
- **🔄 コミット**: `test(frontend): add unit tests for chat components`

**Task 2-4A-3: フックユニットテスト**
- [ ] `tests/frontend/hooks/useChatStream.test.ts` 作成
- [ ] EventSource モック設定
- [ ] ストリーミングロジックテスト
- [ ] エラーケーステスト
- **完了条件**: フックテスト成功、エッジケース対応
- **所要時間**: 35分
- **🔄 コミット**: `test(frontend): add unit tests for useChatStream hook`

### Phase 2-4B: E2Eテスト実装
#### 優先度: 🟢 中

**Task 2-4B-1: Playwright セットアップ**
- [ ] `npm install -D @playwright/test`
- [ ] `playwright.config.ts` 作成
- [ ] ブラウザ設定（Chromium, Firefox, Safari）
- [ ] CI用設定
- **完了条件**: `npx playwright test --ui` でテスト画面表示
- **所要時間**: 20分
- **🔄 コミット**: `test(frontend): setup Playwright for E2E testing`

**Task 2-4B-2: 基本チャットフローE2E**
- [ ] `tests/e2e/basic-chat.spec.ts` 作成
- [ ] チャット画面アクセステスト
- [ ] メッセージ送信・受信テスト
- [ ] ストリーミング表示テスト
- [ ] UI要素存在確認テスト
- **完了条件**: E2Eテスト成功、実際のフロー動作確認
- **所要時間**: 40分
- **🔄 コミット**: `test(frontend): add E2E tests for basic chat flow`

**Task 2-4B-3: エラーケースE2E**
- [ ] ネットワークエラーシミュレーション
- [ ] SSE接続失敗ケース
- [ ] 再接続機能テスト
- [ ] バックエンド停止時の動作
- **完了条件**: エラーケースE2Eテスト成功
- **所要時間**: 30分
- **🔄 コミット**: `test(frontend): add E2E tests for error scenarios`

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
│   │   │   └── layout/
│   │   │       └── Header.tsx
│   │   ├── hooks/               # カスタムフック
│   │   │   └── useChatStream.ts
│   │   ├── lib/                 # ユーティリティ・設定
│   │   │   ├── graphql-client.ts
│   │   │   └── utils.ts
│   │   └── generated/           # GraphQL Code Generator出力
│   │       └── graphql.ts
│   ├── public/                  # 静的ファイル
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   └── codegen.yml
├── tests/                       # 🔧 統合テストフォルダ（ルート直下）
│   ├── frontend/                # フロントエンドテスト
│   │   ├── components/          # コンポーネントテスト
│   │   │   ├── MessageBubble.test.tsx
│   │   │   ├── InputForm.test.tsx
│   │   │   └── LoadingSpinner.test.tsx
│   │   ├── hooks/               # フックテスト
│   │   │   └── useChatStream.test.ts
│   │   └── setup.ts             # テスト設定
│   ├── e2e/                     # E2E テスト
│   │   ├── basic-chat.spec.ts
│   │   └── error-scenarios.spec.ts
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
5. ✅ **Task 2-3B-3完了時**: ストリーミング機能完成後
6. ✅ **Task 2-4A-2完了時**: ユニットテスト完成後
7. ✅ **Task 2-4B-2完了時**: E2Eテスト完成後

**🚨 ファイル削除防止策**:
- 各マイルストーン開始前に `git status` 確認
- 新規ファイル作成後、即座にステージング
- Task完了毎のコミットで作業保護
- `git stash` 活用でWIP保存

---

## 📊 品質目標・完了条件

### Phase 2-1 完了条件
- [ ] Next.js開発サーバー起動成功
- [ ] shadcn/ui コンポーネント使用可能
- [ ] GraphQL型生成成功
- [ ] Apollo Client接続確認

### Phase 2-2 完了条件
- [ ] /chat ページ表示成功
- [ ] 全UIコンポーネント表示確認
- [ ] レスポンシブ対応確認
- [ ] TypeScript エラーゼロ

### Phase 2-3 完了条件
- [ ] GraphQL ask mutation成功
- [ ] SSEストリーミング動作確認
- [ ] エラーハンドリング動作確認
- [ ] フロントエンド・バックエンド統合成功

### Phase 2-4 完了条件
- [ ] ユニットテストカバレッジ >70%
- [ ] E2Eテスト基本フロー成功
- [ ] CI/CDパイプライン緑

### 最終完了条件
- [ ] http://localhost:3000/chat で質問送信・AI応答表示
- [ ] ストリーミング応答のリアルタイム表示
- [ ] 全テスト成功（ユニット・E2E）
- [ ] パフォーマンス目標達成（初回ロード<2秒）

---

## 🚀 更新されたマイルストーン

### Week 1: 基盤構築 + 基本UI
- [x] **ブランチ作成**: `feature/phase-2-ui-streaming`
- [ ] **Task 2-1A**: Next.js + shadcn/ui セットアップ（3タスク）
- [ ] **Task 2-1B**: GraphQL統合基盤（3タスク）
- [ ] **Task 2-2A**: 基本レイアウト（3タスク）
- **🎯 Week 1完了**: /chat ページ表示 + GraphQL接続

### Week 2: コンポーネント実装
- [ ] **Task 2-2B**: チャットUIコンポーネント（4タスク）
- [ ] **Task 2-3A**: GraphQL統合実装（3タスク）
- **🎯 Week 2完了**: 静的チャットUI + GraphQL mutation動作

### Week 3: ストリーミング機能
- [ ] **Task 2-3B**: SSEストリーミング実装（3タスク）
- [ ] 統合テスト・バグ修正
- **🎯 Week 3完了**: リアルタイムチャット機能完成

### Week 4: テスト・仕上げ
- [ ] **Task 2-4A**: ユニットテスト（3タスク）
- [ ] **Task 2-4B**: E2Eテスト（3タスク）
- [ ] パフォーマンス調整・最終統合テスト
- **🎯 Week 4完了**: Phase 2完全完成

---

**🎯 Phase 2完了により、QRAIの基本チャット機能が実際にブラウザで動作可能になります！**

*作成日: 2024-06-09*
*最終更新: 2024-06-09*
