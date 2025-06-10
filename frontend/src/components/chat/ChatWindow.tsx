"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputForm from "./InputForm";
import { LoadingMessage } from "./LoadingSpinner";

// メッセージ型定義
interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  citations?: string[];
  timestamp: Date;
  isStreaming?: boolean;
}

interface ChatWindowProps {
  /** セッションID */
  sessionId?: string;
  /** 初期メッセージ（オプション） */
  initialMessages?: Message[];
  /** メッセージ送信時のコールバック */
  onMessageSend?: (message: string, sessionId?: string) => void;
  /** 最大表示メッセージ数 */
  maxMessages?: number;
}

export default function ChatWindow({
  sessionId,
  initialMessages = [],
  onMessageSend,
  maxMessages = 100,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // 自動スクロール機能
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  };

  // メッセージが更新されたときに自動スクロール
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // メッセージ送信処理
  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content,
      role: "user",
      timestamp: new Date(),
    };

    // ユーザーメッセージを追加
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 外部コールバック実行（実際のAPI呼び出し）
      if (onMessageSend) {
        await onMessageSend(content, sessionId);
      } else {
        // デモ用のダミー応答
        await simulateDemoResponse();
      }
    } catch (error) {
      console.error("メッセージ送信エラー:", error);

      // エラーメッセージを追加
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content:
          "申し訳ございません。エラーが発生しました。もう一度お試しください。",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // デモ用のダミー応答シミュレーション
  const simulateDemoResponse = async () => {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          content:
            "こんにちは！これはデモ応答です。実際のAPIが実装されると、AIからの回答が表示されます。",
          role: "assistant",
          timestamp: new Date(),
          citations: ["https://example.com/doc1", "https://example.com/doc2"],
        };
        setMessages((prev) => [...prev, assistantMessage]);
        resolve();
      }, 1500);
    });
  };

  // メッセージリストの最適化（最大件数制限）
  const displayMessages = messages.slice(-maxMessages);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* メッセージ表示エリア */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-2"
        data-testid="chat-messages"
      >
        {displayMessages.length === 0 ? (
          // 初期状態メッセージ
          <div
            className="flex items-center justify-center h-full text-gray-500"
            data-testid="empty-state"
          >
            <div className="text-center">
              <div className="text-lg font-medium mb-2">QRAIへようこそ</div>
              <div>質問を入力して、AI との会話を始めましょう</div>
            </div>
          </div>
        ) : (
          // メッセージリスト
          displayMessages.map((message) => (
            <MessageBubble
              key={message.id}
              content={message.content}
              role={message.role}
              citations={message.citations}
              isStreaming={message.isStreaming}
              messageId={message.id}
            />
          ))
        )}

        {/* ローディング状態 */}
        {isLoading && <LoadingMessage />}

        {/* 自動スクロール用のマーカー */}
        <div ref={messagesEndRef} />
      </div>

      {/* 入力フォーム */}
      <InputForm
        onSubmit={handleSendMessage}
        isLoading={isLoading}
        placeholder="質問を入力してください..."
        maxLength={1000}
      />
    </div>
  );
}

// 使用例・型エクスポート
export type { Message };
