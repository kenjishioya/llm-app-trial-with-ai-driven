"use client";

import React, { useEffect } from "react";
import Header from "@/components/layout/Header";
import ChatWindow from "@/components/chat/ChatWindow";
import { useChatSession } from "@/hooks/useChatSession";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";

export default function ChatPage() {
  const {
    sessions,
    currentSession,
    createSession,
    isCreating,
    sessionsError,
    currentSessionError,
  } = useChatSession({ autoFetch: true, includeMessages: true });

  // 初回アクセス時に新しいセッションを作成（セッションがない場合）
  useEffect(() => {
    if (sessions.length === 0 && !isCreating) {
      createSession("初回セッション");
    }
  }, [sessions.length, isCreating, createSession]);

  const handleNewSession = async () => {
    await createSession(`新しいチャット ${new Date().toLocaleTimeString()}`);
  };

  return (
    <div className="flex h-screen flex-col">
      <Header />

      <main className="flex-1 overflow-hidden">
        <div className="container h-full max-w-4xl">
          <div className="flex h-full flex-col">
            {/* チャット画面ヘッダー */}
            <div className="border-b px-4 py-3 bg-white flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold">AI Research Assistant</h1>
                <p className="text-sm text-muted-foreground">
                  質問を入力してAIによるリサーチを開始してください
                </p>
                {currentSession && (
                  <p className="text-xs text-gray-500 mt-1">
                    セッション: {currentSession.title}
                  </p>
                )}
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

            {/* エラー表示 */}
            {(sessionsError || currentSessionError) && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 text-sm">
                <strong>接続エラー:</strong>
                {sessionsError?.message || currentSessionError?.message}
              </div>
            )}

            {/* チャットウィンドウ */}
            <div className="flex-1 overflow-hidden">
              {currentSession ? (
                <ChatWindow
                  sessionId={currentSession.id}
                  initialMessages={currentSession.messages.map((msg) => ({
                    id: msg.id,
                    content: msg.content,
                    role: msg.role.toLowerCase() as "user" | "assistant",
                    timestamp: new Date(msg.createdAt),
                    citations: msg.citations
                      ? JSON.parse(msg.citations)
                      : undefined,
                  }))}
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    {isCreating ? (
                      <>
                        <div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-2" />
                        セッションを作成中...
                      </>
                    ) : (
                      <>
                        セッションを読み込み中...
                        <br />
                        <Button
                          onClick={handleNewSession}
                          className="mt-4"
                          variant="outline"
                        >
                          新しいセッションを作成
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
