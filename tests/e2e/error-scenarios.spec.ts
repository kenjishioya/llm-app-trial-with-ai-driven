import { test, expect } from '@playwright/test'

test.describe('エラーケーステスト', () => {
  test.beforeEach(async ({ page }) => {
    // チャットページにアクセス
    await page.goto('/chat')

    // ページが完全に読み込まれるまで待機
    await page.waitForLoadState('networkidle')

    // 「新しいチャットを開始」ボタンが表示されている場合はクリック
    const startChatButton = page.getByRole('button', { name: /新しいチャットを開始|新規チャット/ })
    if (await startChatButton.isVisible()) {
      await startChatButton.click()
      // チャット界面が表示されるまで待機
      await expect(page.getByTestId('message-input')).toBeVisible({ timeout: 10000 })
    }
  })

  test('空文字送信の防止', async ({ page }) => {
    // 空文字の場合、送信ボタンが無効化されることを確認
    await expect(page.getByTestId('send-button')).toBeDisabled()

    // 空白のみ入力
    await page.fill('[data-testid="message-input"]', '   ')
    await expect(page.getByTestId('send-button')).toBeDisabled()

    // 有効なテキストを入力すると送信ボタンが有効化
    await page.fill('[data-testid="message-input"]', 'テストメッセージ')
    await expect(page.getByTestId('send-button')).toBeEnabled()
  })

  test('文字数制限エラー', async ({ page }) => {
    // 非常に長いメッセージを入力
    const longMessage = 'a'.repeat(2000) // 2000文字の長いメッセージ
    await page.fill('[data-testid="message-input"]', longMessage)

    // エラーメッセージが表示されることを確認
    await expect(page.getByTestId('input-error')).toBeVisible({ timeout: 3000 })
    await expect(page.getByTestId('input-error')).toContainText('文字数制限')

    // 送信ボタンが無効化されることを確認
    await expect(page.getByTestId('send-button')).toBeDisabled()

    // 文字数を減らすとエラーが解消
    await page.fill('[data-testid="message-input"]', '適切な長さのメッセージ')
    await expect(page.getByTestId('input-error')).not.toBeVisible()
    await expect(page.getByTestId('send-button')).toBeEnabled()
  })

  test('ネットワークエラーシミュレーション', async ({ page }) => {
    // ネットワークを無効化
    await page.context().setOffline(true)

    // メッセージを送信
    await page.fill('[data-testid="message-input"]', 'ネットワークエラーテスト')
    await page.click('[data-testid="send-button"]')

    // ユーザーメッセージは表示される
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })

    // エラーメッセージまたはエラー状態が表示されることを確認
    // （実装に応じて、エラーメッセージ、再試行ボタン、または接続エラー表示など）
    await expect(
      page.locator('text=エラー').or(
        page.locator('text=接続').or(
          page.locator('text=再試行').or(
            page.getByTestId('connection-error')
          )
        )
      )
    ).toBeVisible({ timeout: 10000 })

    // ネットワークを再有効化
    await page.context().setOffline(false)
  })

  test('GraphQL APIエラー', async ({ page }) => {
    // GraphQL API呼び出しをモック（エラーレスポンス）
    await page.route('**/graphql', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          errors: [{ message: 'Internal Server Error' }]
        })
      })
    })

    // メッセージを送信
    await page.fill('[data-testid="message-input"]', 'GraphQLエラーテスト')
    await page.click('[data-testid="send-button"]')

    // ユーザーメッセージは表示される
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })

    // エラー処理が実行されることを確認
    await expect(
      page.locator('text=エラー').or(
        page.locator('text=問題が発生').or(
          page.getByTestId('error-message')
        )
      )
    ).toBeVisible({ timeout: 10000 })
  })

  test('SSE接続エラー', async ({ page }) => {
    // SSE (EventSource) 接続をモック（失敗）
    await page.route('**/graphql/stream*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'text/plain',
        body: 'Server error'
      })
    })

    // メッセージを送信
    await page.fill('[data-testid="message-input"]', 'SSEエラーテスト')
    await page.click('[data-testid="send-button"]')

    // ユーザーメッセージは表示される
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })

    // SSE接続エラーが処理されることを確認
    // （再接続メッセージ、エラー表示、または代替手段など）
    await expect(
      page.locator('text=接続').or(
        page.locator('text=再接続').or(
          page.locator('text=ストリーミング').or(
            page.getByTestId('streaming-error')
          )
        )
      )
    ).toBeVisible({ timeout: 15000 })
  })

  test('送信中の重複送信防止', async ({ page }) => {
    // 最初のメッセージを送信
    await page.fill('[data-testid="message-input"]', '最初のメッセージ')
    await page.click('[data-testid="send-button"]')

    // 送信中は入力フィールドと送信ボタンが無効化されることを確認
    await expect(page.getByTestId('message-input')).toBeDisabled()
    await expect(page.getByTestId('send-button')).toBeDisabled()

    // 応答が完了するまで無効状態が続くことを確認
    await expect(page.locator('[data-testid*="message-assistant"]')).toBeVisible({ timeout: 30000 })

    // 応答完了後、入力可能になることを確認
    await expect(page.getByTestId('message-input')).toBeEnabled()
    await expect(page.getByTestId('send-button')).toBeDisabled() // 空の状態では無効

    // 新しいメッセージ入力で送信ボタンが有効化
    await page.fill('[data-testid="message-input"]', '2番目のメッセージ')
    await expect(page.getByTestId('send-button')).toBeEnabled()
  })

  test('長時間応答待機でのタイムアウト処理', async ({ page }) => {
    // 極端に遅いレスポンスをシミュレート
    await page.route('**/graphql/stream*', async route => {
      // 長時間レスポンスを返さない
      await new Promise(resolve => setTimeout(resolve, 45000))
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: 'data: {"type": "content", "content": "遅延応答"}\n\n'
      })
    })

    // メッセージを送信
    await page.fill('[data-testid="message-input"]', 'タイムアウトテスト')
    await page.click('[data-testid="send-button"]')

    // ユーザーメッセージは表示される
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })

    // タイムアウトエラーが表示されることを確認（実装に依存）
    await expect(
      page.locator('text=タイムアウト').or(
        page.locator('text=時間切れ').or(
          page.locator('text=応答がありません').or(
            page.getByTestId('timeout-error')
          )
        )
      )
    ).toBeVisible({ timeout: 60000 })
  })

  test('JavaScriptエラーの処理', async ({ page }) => {
    // コンソールエラーを監視
    const consoleErrors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    // ページエラーを監視
    const pageErrors: string[] = []
    page.on('pageerror', error => {
      pageErrors.push(error.message)
    })

    // 正常な操作を実行
    await page.fill('[data-testid="message-input"]', 'JSエラーテスト')
    await page.click('[data-testid="send-button"]')

    // メッセージが送信されることを確認
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })

    // 致命的なJavaScriptエラーが発生していないことを確認
    expect(pageErrors.filter(error =>
      !error.includes('ResizeObserver') && // 無害なブラウザ警告を除外
      !error.includes('favicon')          // faviconエラーを除外
    )).toHaveLength(0)
  })

  test('セッション復旧エラー', async ({ page }) => {
    // 無効なセッションIDでアクセス
    await page.goto('/chat/invalid-session-id')
    await page.waitForLoadState('networkidle')

    // エラー処理が行われることを確認
    // （新しいセッション作成、エラーメッセージ、またはホームリダイレクトなど）
    await expect(
      page.locator('text=セッション').or(
        page.locator('text=見つかりません').or(
          page.locator('text=新しいチャット').or(
            page.getByTestId('session-error')
          )
        )
      )
    ).toBeVisible({ timeout: 10000 })

    // 新しいメッセージが送信可能であることを確認
    await page.fill('[data-testid="message-input"]', 'セッション復旧後テスト')
    await expect(page.getByTestId('send-button')).toBeEnabled()
  })
})
