"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputForm from "./InputForm";
import { LoadingMessage } from "./LoadingSpinner";
import { useAskMutation, AskInput } from "@/generated/graphql";

// メッセージ型定義（GraphQL型に合わせて拡張）
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

  // GraphQL ask mutation フック
  const [askMutation, { loading: mutationLoading, error: mutationError }] =
    useAskMutation({
      onCompleted: (data) => {
        console.log("Ask mutation completed:", data);
        // ストリーミング開始の処理はここで行う予定
      },
      onError: (error) => {
        console.error("Ask mutation error:", error);
        setIsLoading(false);

        // エラーメッセージを追加
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          content: `エラーが発生しました: ${error.message}`,
          role: "assistant",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      },
    });

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

  // メッセージ送信処理（GraphQL統合版）
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
      // GraphQL ask mutation実行
      const askInput: AskInput = {
        question: content,
        sessionId: sessionId || undefined,
        deepResearch: false, // 通常のチャットではfalse
      };

      const result = await askMutation({
        variables: { input: askInput },
      });

      console.log("Ask mutation result:", result);

      // 外部コールバック実行（従来のローディング）
      if (onMessageSend) {
        await onMessageSend(content, sessionId);
      } else {
        // デモ用のダミー応答（実際のストリーミングが実装されるまで）
        await simulateDemoResponse();
      }
    } catch (error) {
      console.error("メッセージ送信エラー:", error);

      // GraphQLエラーの詳細なハンドリング
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content:
          error instanceof Error
            ? `通信エラーが発生しました: ${error.message}`
            : "不明なエラーが発生しました。もう一度お試しください。",
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
            "GraphQL統合テスト: この応答はask mutationを経由して送信されました。実際のストリーミング機能は次のフェーズで実装されます。",
          role: "assistant",
          timestamp: new Date(),
          citations: [
            "https://graphql.org/learn/",
            "https://www.apollographql.com/docs/",
          ],
        };
        setMessages((prev) => [...prev, assistantMessage]);
        resolve();
      }, 1500);
    });
  };

  // メッセージリストの最適化（最大件数制限）
  const displayMessages = messages.slice(-maxMessages);

  // ローディング状態を統合（GraphQL + 従来のローディング）
  const isActuallyLoading = isLoading || mutationLoading;

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* GraphQLエラー表示 */}
      {mutationError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 text-sm">
          <strong>接続エラー:</strong> {mutationError.message}
        </div>
      )}

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
              {sessionId && (
                <div className="text-xs text-gray-400 mt-2">
                  セッション: {sessionId.slice(0, 8)}...
                </div>
              )}
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
        {isActuallyLoading && <LoadingMessage />}

        {/* 自動スクロール用のマーカー */}
        <div ref={messagesEndRef} />
      </div>

      {/* 入力フォーム */}
      <InputForm
        onSubmit={handleSendMessage}
        isLoading={isActuallyLoading}
        placeholder="質問を入力してください..."
        maxLength={1000}
      />
    </div>
  );
}

// 使用例・型エクスポート
export type { Message };
