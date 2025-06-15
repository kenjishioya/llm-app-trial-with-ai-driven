"use client";

import { MessageSquare, X, Edit2, Check, X as XIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SessionType } from "@/generated/graphql";
import { useRouter } from "next/navigation";
import { useState } from "react";

interface SidebarProps {
  isOpen: boolean;
  currentSessionId?: string;
  onSessionSelect: (sessionId: string) => void;
  sessions: SessionType[];
  onDeleteSession: (sessionId: string) => void;
  onUpdateSessionTitle?: (sessionId: string, newTitle: string) => void;
}

export default function Sidebar({
  isOpen,
  currentSessionId,
  onSessionSelect,
  sessions,
  onDeleteSession,
  onUpdateSessionTitle,
}: SidebarProps) {
  const router = useRouter();
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const handleHomeNavigation = () => {
    router.push("/");
  };

  const handleStartEdit = (session: SessionType, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
  };

  const handleSaveEdit = async () => {
    if (editingSessionId && editingTitle.trim() && onUpdateSessionTitle) {
      await onUpdateSessionTitle(editingSessionId, editingTitle.trim());
    }
    setEditingSessionId(null);
    setEditingTitle("");
  };

  const handleCancelEdit = () => {
    setEditingSessionId(null);
    setEditingTitle("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveEdit();
    } else if (e.key === "Escape") {
      handleCancelEdit();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className={`
      h-full bg-white border-r border-gray-200 flex flex-col
      ${isOpen ? "w-80" : "w-0"}
      transition-all duration-300 ease-in-out overflow-hidden
    `}
    >
      {/* ヘッダー */}
      <div className="flex items-center p-4 border-b border-gray-200">
        <div
          className="flex items-center space-x-2 cursor-pointer"
          onClick={handleHomeNavigation}
        >
          <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
            <span className="text-white text-xs font-bold">Q</span>
          </div>
          <span className="text-gray-900 font-semibold">QRAI</span>
        </div>
      </div>

      {/* セッション履歴 */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 pb-4 pt-4">
          <h3 className="text-sm font-medium text-gray-500 mb-2">
            チャット履歴
          </h3>
          <div className="space-y-2">
            {sessions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-sm text-gray-400">履歴はありません</p>
              </div>
            ) : (
              sessions.map((session) => (
                <div
                  key={session.id}
                  className={`
                    group flex items-center justify-between p-2 rounded cursor-pointer
                    transition-colors duration-200
                    ${
                      currentSessionId === session.id
                        ? "bg-blue-50 text-blue-700 border border-blue-200"
                        : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                    }
                  `}
                  onClick={() =>
                    editingSessionId !== session.id &&
                    onSessionSelect(session.id)
                  }
                >
                  <div className="flex items-center space-x-2 min-w-0 flex-1">
                    <MessageSquare className="h-4 w-4 flex-shrink-0" />
                    {editingSessionId === session.id ? (
                      <div className="flex items-center space-x-1 flex-1">
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={handleKeyDown}
                          className="text-sm bg-white border border-gray-300 rounded px-2 py-1 flex-1 min-w-0"
                          autoFocus
                          onClick={(e) => e.stopPropagation()}
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleSaveEdit}
                          className="p-1 h-6 w-6 text-green-600 hover:text-green-700"
                        >
                          <Check className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleCancelEdit}
                          className="p-1 h-6 w-6 text-gray-400 hover:text-gray-600"
                        >
                          <XIcon className="h-3 w-3" />
                        </Button>
                      </div>
                    ) : (
                      <span
                        className="text-sm truncate flex-1"
                        onDoubleClick={(e) => handleStartEdit(session, e)}
                        title="ダブルクリックで編集"
                      >
                        {session.title ||
                          `セッション ${session.id.slice(0, 8)}`}
                      </span>
                    )}
                  </div>
                  {editingSessionId !== session.id && (
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleStartEdit(session, e)}
                        className="p-1 h-6 w-6 text-gray-400 hover:text-blue-500"
                        title="タイトルを編集"
                      >
                        <Edit2 className="h-3 w-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteSession(session.id);
                        }}
                        className="p-1 h-6 w-6 text-gray-400 hover:text-red-500"
                        title="削除"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
