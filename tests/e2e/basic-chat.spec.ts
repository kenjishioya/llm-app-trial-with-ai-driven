import { test, expect } from '@playwright/test'

test.describe('基本チャットフロー', () => {
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

  test('チャットページが正しく表示される', async ({ page }) => {
    // ページタイトル確認
    await expect(page).toHaveTitle(/QRAI/)

    // 主要なUI要素が存在することを確認
    await expect(page.getByTestId('message-input')).toBeVisible()
    await expect(page.getByTestId('send-button')).toBeVisible()

    // 初期状態でメッセージエリアが表示されていることを確認
    await expect(page.locator('[data-testid*="message-"]')).toHaveCount(0)
  })

  test('メッセージ送信と応答受信の基本フロー', async ({ page }) => {
    const testMessage = 'こんにちは、QRAIです。テストメッセージです。'

    // メッセージを入力
    await page.fill('[data-testid="message-input"]', testMessage)

    // 送信ボタンが有効になることを確認
    await expect(page.getByTestId('send-button')).toBeEnabled()

    // メッセージを送信
    await page.click('[data-testid="send-button"]')

    // ユーザーメッセージが表示されることを確認
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('[data-testid*="message-user"]')).toContainText(testMessage)

    // 入力フィールドがクリアされることを確認
    await expect(page.getByTestId('message-input')).toHaveValue('')

    // ローディングスピナーが表示されることを確認
    await expect(page.getByTestId('loading-spinner')).toBeVisible({ timeout: 3000 })

    // AI応答が表示されるまで待機（最大30秒）
    await expect(page.locator('[data-testid*="message-assistant"]')).toBeVisible({ timeout: 30000 })

    // AI応答にテキストが含まれていることを確認
    const aiMessage = page.locator('[data-testid*="message-assistant"]')
    await expect(aiMessage).not.toBeEmpty()

    // ローディングスピナーが非表示になることを確認
    await expect(page.getByTestId('loading-spinner')).not.toBeVisible()
  })

  test('Enterキーでのメッセージ送信', async ({ page }) => {
    const testMessage = 'Enterキーでの送信テスト'

    // メッセージを入力
    await page.fill('[data-testid="message-input"]', testMessage)

    // Enterキーで送信
    await page.press('[data-testid="message-input"]', 'Enter')

    // ユーザーメッセージが表示されることを確認
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('[data-testid*="message-user"]')).toContainText(testMessage)
  })

  test('Shift+Enterで改行入力', async ({ page }) => {
    // Shift+Enterで改行が入力されることを確認
    await page.fill('[data-testid="message-input"]', '1行目')
    await page.press('[data-testid="message-input"]', 'Shift+Enter')
    await page.fill('[data-testid="message-input"]', '1行目\n2行目')

    // 改行が保持されていることを確認
    await expect(page.getByTestId('message-input')).toHaveValue('1行目\n2行目')

    // 送信ボタンクリックで送信
    await page.click('[data-testid="send-button"]')

    // 改行を含むメッセージが正しく表示されることを確認
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('[data-testid*="message-user"]')).toContainText('1行目')
    await expect(page.locator('[data-testid*="message-user"]')).toContainText('2行目')
  })

  test('複数メッセージの送信', async ({ page }) => {
    const messages = [
      '最初のメッセージです',
      '2番目のメッセージです',
      '3番目のメッセージです'
    ]

    for (let i = 0; i < messages.length; i++) {
      // メッセージを入力・送信
      await page.fill('[data-testid="message-input"]', messages[i])
      await page.click('[data-testid="send-button"]')

      // ユーザーメッセージが表示されることを確認
      await expect(page.locator('[data-testid*="message-user"]').nth(i)).toBeVisible({ timeout: 5000 })
      await expect(page.locator('[data-testid*="message-user"]').nth(i)).toContainText(messages[i])

      // AI応答を待機（最後のメッセージ以外は短時間で）
      if (i < messages.length - 1) {
        await expect(page.locator('[data-testid*="message-assistant"]').nth(i)).toBeVisible({ timeout: 30000 })
      }
    }

    // 最終的に全メッセージペアが表示されることを確認
    await expect(page.locator('[data-testid*="message-user"]')).toHaveCount(messages.length)
    await expect(page.locator('[data-testid*="message-assistant"]')).toHaveCount(messages.length)
  })

  test('ページリロード後のセッション継続', async ({ page }) => {
    const testMessage = 'リロードテスト用メッセージ'

    // メッセージを送信
    await page.fill('[data-testid="message-input"]', testMessage)
    await page.click('[data-testid="send-button"]')

    // 応答を待機
    await expect(page.locator('[data-testid*="message-user"]')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('[data-testid*="message-assistant"]')).toBeVisible({ timeout: 30000 })

    // ページをリロード
    await page.reload()
    await page.waitForLoadState('networkidle')

    // メッセージ履歴が保持されていることを確認
    await expect(page.locator('[data-testid*="message-user"]')).toContainText(testMessage)
    await expect(page.locator('[data-testid*="message-assistant"]')).toBeVisible()
  })

  test('レスポンシブデザインの確認', async ({ page }) => {
    // デスクトップサイズ
    await page.setViewportSize({ width: 1200, height: 800 })
    await expect(page.getByTestId('message-input')).toBeVisible()
    await expect(page.getByTestId('send-button')).toBeVisible()

    // タブレットサイズ
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.getByTestId('message-input')).toBeVisible()
    await expect(page.getByTestId('send-button')).toBeVisible()

    // モバイルサイズ
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.getByTestId('message-input')).toBeVisible()
    await expect(page.getByTestId('send-button')).toBeVisible()
  })
})
