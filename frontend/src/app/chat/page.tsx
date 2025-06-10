import React from "react";
import Header from "@/components/layout/Header";
import ChatWindow from "@/components/chat/ChatWindow";

export default function ChatPage() {
  return (
    <div className="flex h-screen flex-col">
      <Header />

      <main className="flex-1 overflow-hidden">
        <div className="container h-full max-w-4xl">
          <div className="flex h-full flex-col">
            {/* チャット画面ヘッダー */}
            <div className="border-b px-4 py-3 bg-white">
              <h1 className="text-xl font-semibold">AI Research Assistant</h1>
              <p className="text-sm text-muted-foreground">
                質問を入力してAIによるリサーチを開始してください
              </p>
            </div>

            {/* チャットウィンドウ */}
            <div className="flex-1 overflow-hidden">
              <ChatWindow />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
