/**
 * Deep Research 進捗バーコンポーネント
 * 状態遷移と進捗パーセンテージを表示
 */

import React from "react";
import { Progress } from "@/components/ui/progress";
import {
  CheckCircle,
  Search,
  Brain,
  FileText,
  AlertCircle,
} from "lucide-react";

interface ProgressBarProps {
  /** 現在の進捗パーセンテージ (0-100) */
  progress: number;
  /** 現在のノード */
  currentNode: string;
  /** 進捗メッセージ */
  messages: string[];
  /** エラーメッセージ */
  error?: string | null;
  /** 完了したかどうか */
  isComplete: boolean;
}

// ノード情報の定義
const NODE_INFO = {
  start: { label: "開始", icon: Search, color: "text-blue-500" },
  retrieve: { label: "検索中", icon: Search, color: "text-blue-500" },
  decide: { label: "判定中", icon: Brain, color: "text-yellow-500" },
  answer: { label: "レポート生成", icon: FileText, color: "text-green-500" },
  complete: { label: "完了", icon: CheckCircle, color: "text-green-600" },
  error: { label: "エラー", icon: AlertCircle, color: "text-red-500" },
} as const;

export default function ProgressBar({
  progress,
  currentNode,
  messages,
  error,
  isComplete,
}: ProgressBarProps) {
  const nodeInfo =
    NODE_INFO[currentNode as keyof typeof NODE_INFO] || NODE_INFO.start;
  const IconComponent = nodeInfo.icon;

  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      {/* ヘッダー */}
      <div className="flex items-center gap-2 mb-3">
        <IconComponent className={`h-5 w-5 ${nodeInfo.color}`} />
        <h3 className="font-medium text-gray-900">Deep Research</h3>
        <span className={`text-sm ${nodeInfo.color}`}>{nodeInfo.label}</span>
      </div>

      {/* 進捗バー */}
      <div className="mb-3">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>進捗状況</span>
          <span>{progress}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* ステップ表示 */}
      <div className="flex justify-between text-xs text-gray-500 mb-3">
        <div
          className={`flex items-center gap-1 ${
            ["start", "retrieve"].includes(currentNode)
              ? "text-blue-600 font-medium"
              : progress > 30
                ? "text-green-600"
                : ""
          }`}
        >
          <Search className="h-3 w-3" />
          <span>検索</span>
        </div>
        <div
          className={`flex items-center gap-1 ${
            currentNode === "decide"
              ? "text-yellow-600 font-medium"
              : progress > 60
                ? "text-green-600"
                : ""
          }`}
        >
          <Brain className="h-3 w-3" />
          <span>判定</span>
        </div>
        <div
          className={`flex items-center gap-1 ${
            ["answer", "complete"].includes(currentNode)
              ? "text-green-600 font-medium"
              : ""
          }`}
        >
          <FileText className="h-3 w-3" />
          <span>レポート</span>
        </div>
      </div>

      {/* エラーメッセージ */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-2 mb-3">
          <div className="flex items-center gap-2 text-red-700">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-medium">エラーが発生しました</span>
          </div>
          <p className="text-sm text-red-600 mt-1">{error}</p>
        </div>
      )}

      {/* 進捗メッセージ */}
      <div className="space-y-1 max-h-32 overflow-y-auto">
        {messages.slice(-5).map((message, index) => (
          <div
            key={index}
            className={`text-sm p-2 rounded ${
              index === messages.length - 1
                ? "bg-blue-50 text-blue-800 border border-blue-200"
                : "text-gray-600"
            }`}
          >
            {message}
          </div>
        ))}
      </div>

      {/* 完了メッセージ */}
      {isComplete && !error && (
        <div className="bg-green-50 border border-green-200 rounded p-2 mt-3">
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm font-medium">
              Deep Research が完了しました
            </span>
          </div>
          <p className="text-sm text-green-600 mt-1">
            詳細なレポートが生成されました。
          </p>
        </div>
      )}
    </div>
  );
}
