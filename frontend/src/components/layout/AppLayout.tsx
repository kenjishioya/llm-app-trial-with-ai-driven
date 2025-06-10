"use client";

import { useState, useCallback } from "react";
import { usePathname } from "next/navigation";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import Sidebar from "./Sidebar";
import { useSession } from "@/components/providers/SessionProvider";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const pathname = usePathname();

  const { sessions, currentSession, createSession, onDeleteSession } =
    useSession();

  const handleSidebarToggle = useCallback(() => {
    setIsSidebarOpen(!isSidebarOpen);
  }, [isSidebarOpen]);

  const handleSessionSelect = useCallback(() => {
    // セッション選択の処理は一旦削除
    // チャットページにリダイレクト
    if (pathname !== "/chat") {
      window.location.href = "/chat";
    }
  }, [pathname]);

  const handleNewChat = useCallback(async () => {
    await createSession(`新しいチャット ${new Date().toLocaleTimeString()}`);
    // チャットページにリダイレクト
    if (pathname !== "/chat") {
      window.location.href = "/chat";
    }
  }, [createSession, pathname]);

  const handleDeleteSession = useCallback(
    async (sessionId: string) => {
      await onDeleteSession(sessionId);
    },
    [onDeleteSession],
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
          onNewChat={handleNewChat}
          sessions={sessions}
          onDeleteSession={handleDeleteSession}
        />
      </div>

      {/* メインコンテンツエリア */}
      <div className="flex-1 bg-gray-50 overflow-hidden flex flex-col">
        {/* 常に表示されるヘッダーバー（ハンバーガーメニュー含む） */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center">
          {!isSidebarOpen && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSidebarToggle}
              className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 mr-3"
            >
              <Menu className="h-5 w-5" />
            </Button>
          )}
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
              <span className="text-white text-xs font-bold">Q</span>
            </div>
            <span className="text-gray-900 font-semibold">QRAI</span>
          </div>
        </div>

        {/* メインコンテンツ */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
