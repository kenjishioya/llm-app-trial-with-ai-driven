import { useCallback, useEffect, useRef, useState } from "react";

/**
 * SSEストリーミングメッセージの型定義
 */
export interface StreamMessage {
  type:
    | "connection_init"
    | "message"
    | "chunk"
    | "complete"
    | "error"
    | "progress";
  data?: string;
  content?: string; // バックエンドのchunkメッセージ用
  messageId?: string;
  sessionId?: string;
  status?: string; // バックエンドのmessageタイプ用
  error?: string;
  progress?: {
    step: number;
    total: number;
    description: string;
  };
}

/**
 * チャットストリーミング状態の型定義
 */
export interface ChatStreamState {
  isConnected: boolean;
  isStreaming: boolean;
  currentMessage: string;
  messageId?: string;
  sessionId?: string;
  error?: string;
  progress?: {
    step: number;
    total: number;
    description: string;
  };
  // 再接続関連
  reconnectAttempts: number;
  isReconnecting: boolean;
}

/**
 * useChatStreamフックの設定オプション
 */
export interface ChatStreamOptions {
  /** 最大再接続試行回数 */
  maxReconnectAttempts?: number;
  /** 再接続間隔（ms） */
  reconnectDelay?: number;
  /** 接続タイムアウト（ms） */
  connectionTimeout?: number;
  /** 自動再接続を有効にするか */
  enableAutoReconnect?: boolean;
}

/**
 * useChatStreamフックの戻り値型
 */
export interface UseChatStreamReturn {
  streamState: ChatStreamState;
  startStream: (
    messageId: string,
    sessionId?: string,
    options?: ChatStreamOptions,
  ) => void;
  stopStream: () => void;
  resetStream: () => void;
  reconnect: () => void;
}

// デフォルト設定
const DEFAULT_OPTIONS: Required<ChatStreamOptions> = {
  maxReconnectAttempts: 3,
  reconnectDelay: 1000,
  connectionTimeout: 30000,
  enableAutoReconnect: true,
};

/**
 * GraphQL over SSE チャットストリーミングフック
 *
 * @description
 * FastAPI GraphQL SSEエンドポイント（/graphql/stream）からのストリーミング応答を受信・管理。
 * 自動再接続、タイムアウト処理、AbortControllerによるメモリリーク防止を提供。
 *
 * @example
 * ```tsx
 * const { streamState, startStream, stopStream, reconnect } = useChatStream();
 *
 * // ストリーミング開始（オプション設定可能）
 * startStream(messageId, sessionId, { maxReconnectAttempts: 5 });
 *
 * // 手動再接続
 * if (streamState.error) {
 *   reconnect();
 * }
 * ```
 */
export const useChatStream = (): UseChatStreamReturn => {
  // ストリーミング状態管理
  const [streamState, setStreamState] = useState<ChatStreamState>({
    isConnected: false,
    isStreaming: false,
    currentMessage: "",
    reconnectAttempts: 0,
    isReconnecting: false,
  });

  // EventSource参照とAbortController（メモリリーク防止）
  const eventSourceRef = useRef<EventSource | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const connectionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 現在の接続パラメータ（再接続用）
  const currentConnectionRef = useRef<{
    messageId: string;
    sessionId?: string;
    options: Required<ChatStreamOptions>;
  } | null>(null);

  /**
   * すべてのタイマーをクリア
   */
  const clearAllTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }
  }, []);

  /**
   * ストリーミング停止
   */
  const stopStream = useCallback(() => {
    // EventSource接続を閉じる
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // AbortController破棄
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    // 全タイマーをクリア
    clearAllTimers();

    // 接続パラメータをクリア
    currentConnectionRef.current = null;

    // ストリーミング状態をリセット
    setStreamState((prev) => ({
      ...prev,
      isConnected: false,
      isStreaming: false,
      isReconnecting: false,
    }));
  }, [clearAllTimers]);

  /**
   * 接続タイムアウト処理
   */
  const handleConnectionTimeout = useCallback(() => {
    console.warn("⏰ SSE接続タイムアウト");
    setStreamState((prev) => ({
      ...prev,
      error: "接続がタイムアウトしました",
      isConnected: false,
      isStreaming: false,
    }));
  }, []);

  /**
   * 再接続を試行
   */
  const attemptReconnect = useCallback(() => {
    const connection = currentConnectionRef.current;
    if (!connection) return;

    const { options } = connection;

    setStreamState((prev) => {
      if (prev.reconnectAttempts >= options.maxReconnectAttempts) {
        console.error("❌ 最大再接続試行回数に達しました");
        return {
          ...prev,
          error: `接続に失敗しました（${options.maxReconnectAttempts}回試行）`,
          isReconnecting: false,
        };
      }

      console.log(
        `🔄 再接続試行 ${prev.reconnectAttempts + 1}/${options.maxReconnectAttempts}`,
      );

      return {
        ...prev,
        reconnectAttempts: prev.reconnectAttempts + 1,
        isReconnecting: true,
        error: undefined,
      };
    });

    // 再接続タイマー設定（指数バックオフ）
    const delay =
      options.reconnectDelay * Math.pow(2, streamState.reconnectAttempts);
    reconnectTimeoutRef.current = setTimeout(() => {
      performConnection(
        connection.messageId,
        connection.sessionId,
        connection.options,
        true,
      );
    }, delay);
  }, [streamState.reconnectAttempts]);

  /**
   * 実際の接続処理
   */
  const performConnection = useCallback(
    (
      messageId: string,
      sessionId?: string,
      options: Required<ChatStreamOptions> = DEFAULT_OPTIONS,
      isReconnection = false,
    ) => {
      // 既存の接続をクリーンアップ
      if (!isReconnection) {
        stopStream();
      }

      // AbortController作成（メモリリーク防止）
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      // 接続パラメータを保存
      currentConnectionRef.current = { messageId, sessionId, options };

      // SSEエンドポイントURL構築
      const baseUrl =
        process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8000";
      const streamUrl = new URL("/graphql/stream", baseUrl);
      streamUrl.searchParams.set("id", messageId);
      if (sessionId) {
        streamUrl.searchParams.set("sessionId", sessionId);
      }

      try {
        // EventSource作成・接続
        const eventSource = new EventSource(streamUrl.toString());
        eventSourceRef.current = eventSource;

        // 接続タイムアウト設定
        connectionTimeoutRef.current = setTimeout(
          handleConnectionTimeout,
          options.connectionTimeout,
        );

        // 接続開始状態に更新
        setStreamState((prev) => ({
          ...prev,
          isConnected: true,
          isStreaming: true,
          messageId,
          sessionId,
          currentMessage: isReconnection ? prev.currentMessage : "", // 再接続時は既存メッセージを保持
          error: undefined,
          isReconnecting: false,
        }));

        // メッセージ受信ハンドラ
        eventSource.onmessage = (event) => {
          // 接続成功したのでタイムアウトをクリア
          if (connectionTimeoutRef.current) {
            clearTimeout(connectionTimeoutRef.current);
            connectionTimeoutRef.current = null;
          }

          try {
            const message: StreamMessage = JSON.parse(event.data);

            switch (message.type) {
              case "connection_init":
                console.log("🔗 SSE接続初期化完了");
                // 再接続成功時は試行回数をリセット
                setStreamState((prev) => ({
                  ...prev,
                  reconnectAttempts: 0,
                  isReconnecting: false,
                }));
                break;

              case "message":
                // メッセージ処理開始通知
                console.log("📝 メッセージ処理開始:", message.status);
                setStreamState((prev) => ({
                  ...prev,
                  isStreaming: true,
                  messageId: message.messageId,
                  sessionId: message.sessionId,
                }));
                break;

              case "chunk":
                // テキストチャンクを段階的に追加
                const chunkContent = message.content || message.data || "";
                if (chunkContent) {
                  setStreamState((prev) => ({
                    ...prev,
                    currentMessage: prev.currentMessage + chunkContent,
                  }));
                }
                break;

              case "complete":
                // ストリーミング完了
                console.log("✅ SSEストリーミング完了");
                clearAllTimers();
                setStreamState((prev) => ({
                  ...prev,
                  isStreaming: false,
                  reconnectAttempts: 0,
                  isReconnecting: false,
                }));
                // 接続は維持（再利用可能）
                break;

              case "progress":
                // Deep Research進捗更新
                if (message.progress) {
                  setStreamState((prev) => ({
                    ...prev,
                    progress: message.progress,
                  }));
                }
                break;

              case "error":
                // エラー発生
                console.error("❌ SSEストリーミングエラー:", message.error);
                clearAllTimers();
                setStreamState((prev) => ({
                  ...prev,
                  isStreaming: false,
                  error:
                    message.error || "ストリーミング中にエラーが発生しました",
                }));

                // サーバーエラーの場合は再接続を試行
                if (options.enableAutoReconnect) {
                  attemptReconnect();
                }
                break;

              default:
                console.warn("⚠️ 未知のSSEメッセージタイプ:", message.type);
            }
          } catch (parseError) {
            console.error("❌ SSEメッセージ解析エラー:", parseError);
            setStreamState((prev) => ({
              ...prev,
              error: "メッセージの解析に失敗しました",
            }));
          }
        };

        // 接続エラーハンドラ
        eventSource.onerror = (event) => {
          console.error("❌ SSE接続エラー:", event);
          clearAllTimers();

          // 接続状態が閉じられた場合
          if (eventSource.readyState === EventSource.CLOSED) {
            setStreamState((prev) => ({
              ...prev,
              isConnected: false,
              isStreaming: false,
              error: "サーバーとの接続が切断されました",
            }));

            // 自動再接続を試行
            if (options.enableAutoReconnect) {
              attemptReconnect();
            }
          } else if (eventSource.readyState === EventSource.CONNECTING) {
            console.log("🔄 SSE再接続中...");
            setStreamState((prev) => ({
              ...prev,
              isReconnecting: true,
            }));
          }
        };

        // Abort時のクリーンアップ
        abortController.signal.addEventListener("abort", () => {
          eventSource.close();
          clearAllTimers();
          setStreamState((prev) => ({
            ...prev,
            isConnected: false,
            isStreaming: false,
            isReconnecting: false,
          }));
        });
      } catch (error) {
        console.error("❌ SSE接続開始エラー:", error);
        clearAllTimers();
        setStreamState((prev) => ({
          ...prev,
          error: "接続の開始に失敗しました",
          isReconnecting: false,
        }));

        // 接続開始エラーでも再接続を試行
        if (options.enableAutoReconnect) {
          attemptReconnect();
        }
      }
    },
    [clearAllTimers, handleConnectionTimeout, attemptReconnect, stopStream],
  );

  /**
   * ストリーミング開始
   */
  const startStream = useCallback(
    (messageId: string, sessionId?: string, options?: ChatStreamOptions) => {
      const mergedOptions = { ...DEFAULT_OPTIONS, ...options };
      performConnection(messageId, sessionId, mergedOptions);
    },
    [performConnection],
  );

  /**
   * ストリーミング状態をリセット
   */
  const resetStream = useCallback(() => {
    stopStream();
    setStreamState({
      isConnected: false,
      isStreaming: false,
      currentMessage: "",
      reconnectAttempts: 0,
      isReconnecting: false,
    });
  }, [stopStream]);

  /**
   * 手動再接続
   */
  const reconnect = useCallback(() => {
    const connection = currentConnectionRef.current;
    if (!connection) {
      console.warn("⚠️ 再接続用の接続情報がありません");
      return;
    }

    console.log("🔄 手動再接続を開始");

    // 再接続試行回数をリセットして再接続
    setStreamState((prev) => ({ ...prev, reconnectAttempts: 0 }));
    performConnection(
      connection.messageId,
      connection.sessionId,
      connection.options,
      true,
    );
  }, [performConnection]);

  // コンポーネントアンマウント時のクリーンアップ
  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return {
    streamState,
    startStream,
    stopStream,
    resetStream,
    reconnect,
  };
};
