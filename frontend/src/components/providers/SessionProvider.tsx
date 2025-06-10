"use client";

import React, { createContext, useContext } from "react";
import { useChatSession } from "@/hooks/useChatSession";
import { SessionType } from "@/generated/graphql";

interface SessionContextType {
  sessions: SessionType[];
  currentSession?: SessionType;
  isCreating: boolean;
  createSession: (title?: string) => Promise<SessionType | undefined>;
  onDeleteSession: (sessionId: string) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const { sessions, currentSession, createSession, deleteSession, isCreating } =
    useChatSession({
      autoFetch: true,
      includeMessages: false,
    });

  const handleDeleteSession = async (sessionId: string) => {
    await deleteSession(sessionId);
  };

  const handleCreateSession = async (title = "新しいセッション") => {
    return await createSession(title);
  };

  return (
    <SessionContext.Provider
      value={{
        sessions: sessions || [],
        currentSession,
        isCreating,
        createSession: handleCreateSession,
        onDeleteSession: handleDeleteSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
