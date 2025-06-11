# E2E Tests

このディレクトリは**エンドツーエンドテスト**専用です。

## 用途
- フロントエンド ↔ バックエンド統合テスト
- ブラウザ操作テスト (Playwright)
- 全体フローテスト

## テストカテゴリ別配置
- **バックエンドテスト**: `backend/tests/`
- **フロントエンドテスト**: `frontend/__tests__/`
- **E2Eテスト**: `tests/e2e/` (ここ)

## 実行方法
```bash
# E2Eテストのみ実行
npm run test:e2e

# または
playwright test tests/e2e/
```
