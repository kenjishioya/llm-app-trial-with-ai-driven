"use client";

import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import InputForm from "./InputForm";
import ProgressBar from "./ProgressBar";
import { LoadingMessage } from "./LoadingSpinner";
import { useAskMutation, AskInput } from "@/generated/graphql";
import { useChatStream } from "@/hooks/useChatStream";
import { useDeepResearch } from "@/hooks/useDeepResearch";

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

  // SSE ストリーミングフック
  const { streamState, startStream, stopStream, resetStream } = useChatStream();

  // Deep Research フック
  const {
    startDeepResearch,
    isLoading: isDeepResearching,
    error: deepResearchError,
    progress: deepResearchProgress,
    currentProgress,
    currentNode,
    isComplete: isDeepResearchComplete,
    finalReport,
    reset: resetDeepResearch,
  } = useDeepResearch();

  // GraphQL ask mutation フック
  const [askMutation, { loading: mutationLoading, error: mutationError }] =
    useAskMutation({
      onCompleted: (data) => {
        console.log("✅ Ask mutation completed:", data);

        // ストリーミング開始
        if (data.ask.messageId) {
          console.log(
            "🚀 Starting SSE stream for messageId:",
            data.ask.messageId,
          );
          startStream(data.ask.messageId, data.ask.sessionId || sessionId);
        } else {
          console.warn("⚠️ No messageId returned from ask mutation");
          setIsLoading(false);
        }
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

  // SSE ストリーミング状態の監視・メッセージ更新
  useEffect(() => {
    if (streamState.isStreaming && streamState.currentMessage) {
      // ストリーミング中のメッセージを更新または作成
      setMessages((prev) => {
        const lastMessage = prev[prev.length - 1];

        // 最後のメッセージがAIからのストリーミングメッセージの場合は更新
        if (
          lastMessage &&
          lastMessage.role === "assistant" &&
          lastMessage.isStreaming &&
          streamState.messageId &&
          lastMessage.id === `streaming-${streamState.messageId}`
        ) {
          return prev.map((msg, index) =>
            index === prev.length - 1
              ? { ...msg, content: streamState.currentMessage }
              : msg,
          );
        } else {
          // 新しいストリーミングメッセージを作成
          const streamingMessage: Message = {
            id: `streaming-${streamState.messageId || Date.now()}`,
            content: streamState.currentMessage,
            role: "assistant",
            timestamp: new Date(),
            isStreaming: true,
          };
          return [...prev, streamingMessage];
        }
      });
    }
  }, [
    streamState.currentMessage,
    streamState.isStreaming,
    streamState.messageId,
  ]);

  // ストリーミング完了時の処理
  useEffect(() => {
    if (
      !streamState.isStreaming &&
      streamState.currentMessage &&
      streamState.messageId
    ) {
      console.log("✅ Streaming completed");

      // ストリーミングメッセージを最終化（isStreamingをfalseに）
      setMessages((prev) => {
        return prev.map((msg) => {
          if (
            msg.id === `streaming-${streamState.messageId}` &&
            msg.isStreaming
          ) {
            return {
              ...msg,
              id: `assistant-${streamState.messageId}`, // 最終的なIDに変更
              isStreaming: false,
            };
          }
          return msg;
        });
      });

      setIsLoading(false);

      // ストリーミング状態をリセット
      resetStream();
    }
  }, [
    streamState.isStreaming,
    streamState.currentMessage,
    streamState.messageId,
    resetStream,
  ]);

  // ストリーミングエラー処理
  useEffect(() => {
    if (streamState.error) {
      console.error("❌ Streaming error:", streamState.error);
      setIsLoading(false);

      // エラーメッセージを追加
      const errorMessage: Message = {
        id: `stream-error-${Date.now()}`,
        content: `ストリーミングエラー: ${streamState.error}`,
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);

      // エラー状態をリセット
      resetStream();
    }
  }, [streamState.error, resetStream]);

  // Deep Research完了時の処理
  useEffect(() => {
    if (isDeepResearchComplete && finalReport) {
      console.log("✅ Deep Research completed");

      // レポートメッセージを追加
      const reportMessage: Message = {
        id: `deep-research-${Date.now()}`,
        content: finalReport,
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, reportMessage]);

      // Deep Research状態をリセット
      resetDeepResearch();
    }
  }, [isDeepResearchComplete, finalReport, resetDeepResearch]);

  // Deep Researchエラー処理
  useEffect(() => {
    if (deepResearchError) {
      console.error("❌ Deep Research error:", deepResearchError);

      // エラーメッセージを追加
      const errorMessage: Message = {
        id: `deep-research-error-${Date.now()}`,
        content: `Deep Research エラー: ${deepResearchError}`,
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);

      // エラー状態をリセット
      resetDeepResearch();
    }
  }, [deepResearchError, resetDeepResearch]);

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

  // メッセージ送信処理（GraphQL + SSE統合版）
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
      // 既存のストリーミングがある場合は停止
      if (streamState.isStreaming) {
        stopStream();
      }

      // GraphQL ask mutation実行
      const askInput: AskInput = {
        question: content,
        sessionId: sessionId || undefined,
        deepResearch: false, // 通常のチャットではfalse
      };

      await askMutation({
        variables: { input: askInput },
      });

      // GraphQL mutationが成功すれば、onCompletedでストリーミングが開始される
    } catch (error) {
      console.error("メッセージ送信エラー:", error);
      setIsLoading(false);

      // エラーメッセージの追加
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
    }
  };

  // Deep Research実行処理
  const handleDeepResearch = async (question: string) => {
    if (!sessionId) {
      console.error("❌ Session ID is required for Deep Research");
      return;
    }

    const userMessage: Message = {
      id: `user-deep-research-${Date.now()}`,
      content: `🔍 Deep Research: ${question}`,
      role: "user",
      timestamp: new Date(),
    };

    // ユーザーメッセージを追加
    setMessages((prev) => [...prev, userMessage]);

    try {
      // Deep Research開始
      await startDeepResearch(question, sessionId);
    } catch (error) {
      console.error("Deep Research開始エラー:", error);

      // エラーメッセージの追加
      const errorMessage: Message = {
        id: `deep-research-start-error-${Date.now()}`,
        content:
          error instanceof Error
            ? `Deep Research開始エラー: ${error.message}`
            : "Deep Researchの開始に失敗しました。もう一度お試しください。",
        role: "assistant",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  // メッセージリストの最適化（最大件数制限）
  const displayMessages = messages.slice(-maxMessages);

  // ローディング状態を統合（GraphQL + ストリーミング + Deep Research + 従来のローディング）
  const isActuallyLoading =
    isLoading ||
    mutationLoading ||
    streamState.isStreaming ||
    isDeepResearching;

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* GraphQLエラー表示 */}
      {mutationError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 text-sm">
          <strong>接続エラー:</strong> {mutationError.message}
        </div>
      )}

      {/* ストリーミングエラー表示 */}
      {streamState.error && (
        <div className="bg-orange-50 border border-orange-200 text-orange-700 px-4 py-2 text-sm">
          <strong>ストリーミングエラー:</strong> {streamState.error}
        </div>
      )}

      {/* Deep Research進捗表示 */}
      {(isDeepResearching || isDeepResearchComplete) && (
        <div className="p-4 border-b">
          <ProgressBar
            progress={currentProgress}
            currentNode={currentNode}
            messages={deepResearchProgress.map((p) => p.content)}
            error={deepResearchError}
            isComplete={isDeepResearchComplete}
          />
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
        {isActuallyLoading && !streamState.currentMessage && <LoadingMessage />}

        {/* 自動スクロール用のマーカー */}
        <div ref={messagesEndRef} />
      </div>

      {/* 入力フォーム */}
      <InputForm
        onSubmit={handleSendMessage}
        onDeepResearch={handleDeepResearch}
        isLoading={isActuallyLoading}
        isDeepResearching={isDeepResearching}
        placeholder="質問を入力してください..."
        maxLength={1000}
      />
    </div>
  );
}

// コンポーネントのアンマウント時にストリーミングをクリーンアップ（追加セーフティ）
export function useChatWindowCleanup() {
  const { stopStream } = useChatStream();

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);
}

// 使用例・型エクスポート
export type { Message };
