import React from "react";
import Header from "@/components/layout/Header";

export default function ChatPage() {
  return (
    <div className="flex h-screen flex-col">
      <Header />

      <main className="flex-1 overflow-hidden">
        <div className="container h-full max-w-4xl">
          <div className="flex h-full flex-col">
            {/* チャット画面ヘッダー */}
            <div className="border-b px-4 py-3">
              <h1 className="text-xl font-semibold">AI Research Assistant</h1>
              <p className="text-sm text-muted-foreground">
                質問を入力してAIによるリサーチを開始してください
              </p>
            </div>

            {/* メッセージエリア（プレースホルダー） */}
            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-4">
                {/* プレースホルダーメッセージ */}
                <div className="flex justify-center">
                  <div className="rounded-lg bg-muted p-6 text-center max-w-md">
                    <h2 className="text-lg font-medium mb-2">
                      QRAIへようこそ！
                    </h2>
                    <p className="text-muted-foreground">
                      下の入力欄に質問を入力すると、AIが調査して回答します。
                    </p>
                  </div>
                </div>

                {/* サンプルメッセージ（ユーザー） */}
                <div className="flex justify-end">
                  <div className="max-w-[70%] rounded-lg bg-primary p-3 text-primary-foreground">
                    <p>最新のAI技術トレンドについて教えてください</p>
                  </div>
                </div>

                {/* サンプルメッセージ（アシスタント） */}
                <div className="flex justify-start">
                  <div className="max-w-[70%] rounded-lg bg-muted p-3">
                    <p>
                      最新のAI技術トレンドについて調査いたします。
                      現在、生成AI、マルチモーダルAI、AIエージェントなどが注目されています...
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">
                      ※ これはプレースホルダーメッセージです
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 入力エリア（プレースホルダー） */}
            <div className="border-t p-4">
              <div className="flex space-x-2">
                <div className="flex-1">
                  <textarea
                    placeholder="ここに質問を入力してください..."
                    className="w-full resize-none rounded-md border px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    rows={3}
                    disabled
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    ※ 入力機能は次のタスクで実装されます
                  </p>
                </div>
                <button
                  className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                  disabled
                >
                  送信
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
