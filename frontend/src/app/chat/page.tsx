"use client";

import ChatWindow from "@/components/chat/ChatWindow";
import { useSession } from "@/components/providers/SessionProvider";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";

export default function ChatPage() {
  const { currentSession, createSession, isCreating } = useSession();

  const handleNewSession = async () => {
    await createSession(`新しいチャット ${new Date().toLocaleTimeString()}`);
  };

  // セッションがない場合の初期画面
  if (!currentSession) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl text-blue-600 font-bold">Q</span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              AI Research Assistant
            </h2>
            <p className="text-gray-600">
              新しいチャットを開始して、AIによるリサーチを始めましょう
            </p>
          </div>
          <Button
            onClick={handleNewSession}
            disabled={isCreating}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            {isCreating ? "作成中..." : "新しいチャットを開始"}
          </Button>
        </div>
      </div>
    );
  }

  // セッションがある場合の通常の画面
  return (
    <div className="flex h-full flex-col bg-white">
      {/* チャット画面ヘッダー */}
      <div className="border-b px-6 py-4 bg-white flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            AI Research Assistant
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            質問を入力してAIによるリサーチを開始してください
          </p>
          <p className="text-xs text-gray-500 mt-1">
            セッション: {currentSession.title}
          </p>
        </div>

        {/* 新しいセッション作成ボタン */}
        <Button
          onClick={handleNewSession}
          disabled={isCreating}
          variant="outline"
          size="sm"
          className="gap-2"
        >
          <PlusIcon className="h-4 w-4" />
          {isCreating ? "作成中..." : "新規チャット"}
        </Button>
      </div>

      {/* チャットウィンドウ */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow
          sessionId={currentSession.id}
          initialMessages={currentSession.messages.map((msg) => ({
            id: msg.id,
            content: msg.content,
            role: msg.role.toLowerCase() as "user" | "assistant",
            timestamp: new Date(msg.createdAt),
            citations: msg.citations ? JSON.parse(msg.citations) : undefined,
          }))}
        />
      </div>
    </div>
  );
}
