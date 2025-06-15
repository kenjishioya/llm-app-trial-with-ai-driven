"use client";

import { useState, useCallback } from "react";
import { usePathname, useRouter } from "next/navigation";
import { gql } from "@apollo/client";
import Sidebar from "./Sidebar";
import { useSession } from "@/components/providers/SessionProvider";
import { useUpdateSessionTitleMutation } from "@/generated/graphql";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarOpen] = useState(true);
  const pathname = usePathname();
  const router = useRouter();

  const { sessions, currentSession, onDeleteSession, selectSession } =
    useSession();

  // セッションタイトル更新mutation
  const [updateSessionTitleMutation] = useUpdateSessionTitleMutation({
    onCompleted: (data) => {
      console.log("セッションタイトル更新完了:", data);
    },
    onError: (error) => {
      console.error("セッションタイトル更新エラー:", error);
    },
    // Apollo Cacheを更新
    update(cache, { data }) {
      if (data?.updateSessionTitle) {
        const updatedSession = data.updateSessionTitle;

        // キャッシュ内のセッションを更新
        cache.modify({
          fields: {
            sessions(existingSessions = [], { readField }) {
              return existingSessions.map((sessionRef: any) => {
                if (readField("id", sessionRef) === updatedSession.id) {
                  // セッションのタイトルを更新
                  cache.writeFragment({
                    id: cache.identify(sessionRef),
                    fragment: gql`
                      fragment UpdatedSession on SessionType {
                        title
                        updatedAt
                      }
                    `,
                    data: {
                      title: updatedSession.title,
                      updatedAt: updatedSession.updatedAt,
                    },
                  });
                }
                return sessionRef;
              });
            },
          },
        });
      }
    },
  });

  const handleSessionSelect = useCallback(
    (sessionId: string) => {
      // セッションを選択
      selectSession(sessionId);

      // チャットページに移動（現在のページがチャットページでない場合）
      if (pathname !== "/chat") {
        router.push("/chat");
      }
    },
    [selectSession, pathname, router],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: string) => {
      await onDeleteSession(sessionId);
    },
    [onDeleteSession],
  );

  const handleUpdateSessionTitle = useCallback(
    async (sessionId: string, newTitle: string) => {
      try {
        await updateSessionTitleMutation({
          variables: {
            id: sessionId,
            input: { title: newTitle },
          },
        });
      } catch (error) {
        console.error("セッションタイトル更新失敗:", error);
      }
    },
    [updateSessionTitleMutation],
  );

  return (
    <div className="flex h-screen">
      {/* サイドバー */}
      <div
        className={`
        ${isSidebarOpen ? "w-80" : "w-0"}
        transition-all duration-300 ease-in-out overflow-hidden
      `}
      >
        <Sidebar
          isOpen={isSidebarOpen}
          currentSessionId={currentSession?.id}
          onSessionSelect={handleSessionSelect}
          sessions={sessions}
          onDeleteSession={handleDeleteSession}
          onUpdateSessionTitle={handleUpdateSessionTitle}
        />
      </div>

      {/* メインコンテンツエリア */}
      <div className="flex-1 bg-gray-50 overflow-hidden flex flex-col">
        {/* メインコンテンツ */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
