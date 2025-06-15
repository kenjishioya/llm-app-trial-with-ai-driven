import { useState } from "react";
import {
  useCreateSessionMutation,
  useDeleteSessionMutation,
  useGetSessionsQuery,
  useGetSessionQuery,
  SessionInput,
  SessionType,
  GetSessionsDocument,
} from "@/generated/graphql";
import { Reference } from "@apollo/client";

interface UseChatSessionProps {
  /** セッション一覧を自動取得するか */
  autoFetch?: boolean;
  /** メッセージも含めて取得するか */
  includeMessages?: boolean;
}

interface UseChatSessionReturn {
  // セッション一覧
  sessions: SessionType[];
  sessionsLoading: boolean;
  sessionsError?: Error;

  // 現在のセッション
  currentSession?: SessionType;
  currentSessionLoading: boolean;
  currentSessionError?: Error;

  // セッション操作
  createSession: (title?: string) => Promise<SessionType | undefined>;
  deleteSession: (id: string) => Promise<boolean>;
  selectSession: (id: string) => void;

  // 状態
  isCreating: boolean;
  isDeleting: boolean;
}

/**
 * セッション管理のためのカスタムフック
 * GraphQL mutations/queries を抽象化し、セッション操作を簡単にする
 */
export function useChatSession({
  autoFetch = true,
  includeMessages = false,
}: UseChatSessionProps = {}): UseChatSessionReturn {
  const [currentSessionId, setCurrentSessionId] = useState<string>();

  // セッション一覧取得
  const {
    data: sessionsData,
    loading: sessionsLoading,
    error: sessionsError,
  } = useGetSessionsQuery({
    variables: { includeMessages },
    skip: !autoFetch,
    fetchPolicy: "cache-first",
    errorPolicy: "all",
  });

  // 現在のセッション詳細取得
  const {
    data: currentSessionData,
    loading: currentSessionLoading,
    error: currentSessionError,
  } = useGetSessionQuery({
    variables: { id: currentSessionId! },
    skip: !currentSessionId,
    fetchPolicy: "cache-and-network",
  });

  // セッション作成mutation
  const [createSessionMutation, { loading: isCreating }] =
    useCreateSessionMutation({
      onCompleted: (data) => {
        // 作成したセッションを選択
        setCurrentSessionId(data.createSession.id);
      },
      onError: (error) => {
        console.error("セッション作成エラー:", error);
      },
      // キャッシュを自動更新
      update(cache, { data }) {
        if (data?.createSession) {
          const newSession = {
            ...data.createSession,
            messages: [], // 新しいセッションはメッセージが空
          };
          try {
            // 既存のセッション一覧を取得
            const existingData = cache.readQuery<{ sessions: SessionType[] }>({
              query: GetSessionsDocument,
              variables: { includeMessages },
            });

            if (existingData?.sessions) {
              // 新しいセッションを先頭に追加
              cache.writeQuery({
                query: GetSessionsDocument,
                variables: { includeMessages },
                data: {
                  sessions: [newSession, ...existingData.sessions],
                },
              });
            }
          } catch {
            // キャッシュが存在しない場合は modify を使用
            cache.modify({
              fields: {
                sessions(existingSessions = []) {
                  return [newSession, ...existingSessions];
                },
              },
            });
          }
        }
      },
    });

  // セッション削除mutation
  const [deleteSessionMutation, { loading: isDeleting }] =
    useDeleteSessionMutation({
      onCompleted: () => {},
      onError: (error) => {
        console.error("セッション削除エラー:", error);
      },
      // キャッシュから削除
      update(cache, { data }, { variables }) {
        if (data?.deleteSession && variables?.id) {
          cache.modify({
            fields: {
              sessions(existingSessions = [], { readField }) {
                return existingSessions.filter(
                  (sessionRef: Reference) =>
                    readField("id", sessionRef) !== variables.id,
                );
              },
            },
          });
        }
      },
    });

  // セッション作成
  const createSession = async (
    title?: string,
  ): Promise<SessionType | undefined> => {
    // 既に作成中の場合は処理を中断
    if (isCreating) {
      return undefined;
    }

    try {
      const input: SessionInput = {
        title: title || `新しいセッション ${new Date().toLocaleString()}`,
      };

      const result = await createSessionMutation({
        variables: { input },
      });

      return result.data?.createSession as SessionType;
    } catch (error) {
      console.error("セッション作成失敗:", error);
      return undefined;
    }
  };

  // セッション削除
  const deleteSession = async (id: string): Promise<boolean> => {
    try {
      const result = await deleteSessionMutation({
        variables: { id },
      });

      return result.data?.deleteSession ?? false;
    } catch (error) {
      console.error("セッション削除失敗:", error);
      return false;
    }
  };

  // セッション選択
  const selectSession = (id: string) => {
    setCurrentSessionId(id);
  };

  return {
    // セッション一覧
    sessions: (sessionsData?.sessions ?? []) as SessionType[],
    sessionsLoading,
    sessionsError: sessionsError ? new Error(sessionsError.message) : undefined,

    // 現在のセッション
    currentSession: currentSessionData?.session as SessionType | undefined,
    currentSessionLoading,
    currentSessionError: currentSessionError
      ? new Error(currentSessionError.message)
      : undefined,

    // セッション操作
    createSession,
    deleteSession,
    selectSession,

    // 状態
    isCreating,
    isDeleting,
  };
}
