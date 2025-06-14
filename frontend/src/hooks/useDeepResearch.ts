/**
 * Deep Research フック
 * GraphQL mutation と subscription を使用して Deep Research 機能を提供
 */

import { useState, useCallback, useEffect } from "react";
import {
  useDeepResearchMutation,
  useStreamDeepResearchSubscription,
  DeepResearchInput,
  DeepResearchProgress as GraphQLDeepResearchProgress,
} from "@/generated/graphql";

// 型定義
export interface DeepResearchProgress {
  content: string;
  researchId: string;
  sessionId: string;
  isComplete: boolean;
  currentNode: string;
  progressPercentage: number;
}

export interface DeepResearchResult {
  sessionId: string;
  researchId: string;
  streamUrl: string;
  status: string;
  message?: string;
}

export interface UseDeepResearchReturn {
  /** Deep Research を開始 */
  startDeepResearch: (question: string, sessionId: string) => Promise<void>;
  /** 実行中かどうか */
  isLoading: boolean;
  /** エラー */
  error: string | null;
  /** 進捗データ */
  progress: DeepResearchProgress[];
  /** 現在の進捗パーセンテージ */
  currentProgress: number;
  /** 現在のノード */
  currentNode: string;
  /** 完了したかどうか */
  isComplete: boolean;
  /** 最終レポート */
  finalReport: string | null;
  /** リセット */
  reset: () => void;
}

export function useDeepResearch(): UseDeepResearchReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<DeepResearchProgress[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentNode, setCurrentNode] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [finalReport, setFinalReport] = useState<string | null>(null);

  // Subscription用の状態
  const [researchId, setResearchId] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);

  // GraphQL Mutation
  const [deepResearchMutation] = useDeepResearchMutation({
    onCompleted: (data) => {
      console.log("Deep Research mutation completed:", data);

      if (data.deepResearch.status === "error") {
        setError(data.deepResearch.message || "Deep Research failed");
        setIsLoading(false);
        return;
      }

      if (data.deepResearch.researchId) {
        // Subscription開始のための状態設定
        setResearchId(data.deepResearch.researchId);
        console.log("Deep Research started, waiting for subscription...");
      } else {
        setError("No research ID returned from mutation");
        setIsLoading(false);
      }
    },
    onError: (err) => {
      console.error("Deep Research mutation error:", err);
      setError(err.message);
      setIsLoading(false);
    },
  });

  // GraphQL Subscription
  const { data: subscriptionData, error: subscriptionError } =
    useStreamDeepResearchSubscription({
      variables: {
        researchId: researchId || "",
        sessionId: currentSessionId || "",
        question: currentQuestion || "",
      },
      skip: !researchId || !currentSessionId || !currentQuestion,
      onError: (err) => {
        console.error("Deep Research subscription error:", err);
        setError(err.message);
        setIsLoading(false);
      },
    });

  // Subscription データの処理
  useEffect(() => {
    if (subscriptionData?.streamDeepResearch) {
      const progressData = subscriptionData.streamDeepResearch;

      console.log("Deep Research progress:", progressData);

      // GraphQL型をローカル型に変換
      const localProgressData: DeepResearchProgress = {
        content: progressData.content,
        researchId: progressData.researchId,
        sessionId: progressData.sessionId,
        isComplete: progressData.isComplete,
        currentNode: progressData.currentNode,
        progressPercentage: progressData.progressPercentage,
      };

      // 進捗データを追加
      setProgress((prev) => [...prev, localProgressData]);
      setCurrentProgress(progressData.progressPercentage);
      setCurrentNode(progressData.currentNode);

      // 完了チェック
      if (progressData.isComplete) {
        setIsComplete(true);
        setIsLoading(false);

        // 最終レポートを設定（contentが長い場合はレポートとして扱う）
        if (progressData.content.length > 200) {
          setFinalReport(progressData.content);
        }
      }
    }
  }, [subscriptionData]);

  // Subscription エラーの処理
  useEffect(() => {
    if (subscriptionError) {
      console.error("Deep Research subscription error:", subscriptionError);
      setError(subscriptionError.message);
      setIsLoading(false);
    }
  }, [subscriptionError]);

  const startDeepResearch = useCallback(
    async (question: string, sessionId: string) => {
      try {
        setIsLoading(true);
        setError(null);
        setProgress([]);
        setCurrentProgress(0);
        setCurrentNode("");
        setIsComplete(false);
        setFinalReport(null);

        console.log("Starting Deep Research:", { question, sessionId });

        // Subscription用の状態を設定
        setCurrentSessionId(sessionId);
        setCurrentQuestion(question);

        // Deep Research Mutation を実行
        const input: DeepResearchInput = {
          question,
          sessionId,
        };

        await deepResearchMutation({
          variables: { input },
        });
      } catch (err) {
        console.error("Deep Research start error:", err);
        setError(err instanceof Error ? err.message : "Unknown error occurred");
        setIsLoading(false);
      }
    },
    [deepResearchMutation],
  );

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setProgress([]);
    setCurrentProgress(0);
    setCurrentNode("");
    setIsComplete(false);
    setFinalReport(null);
    setResearchId(null);
    setCurrentSessionId(null);
    setCurrentQuestion(null);
  }, []);

  return {
    startDeepResearch,
    isLoading,
    error,
    progress,
    currentProgress,
    currentNode,
    isComplete,
    finalReport,
    reset,
  };
}
