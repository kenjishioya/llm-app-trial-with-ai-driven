"use client";

import { useState, useRef, FormEvent, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Search } from "lucide-react";

interface InputFormProps {
  /** メッセージ送信コールバック */
  onSubmit: (message: string) => void;
  /** Deep Research実行コールバック */
  onDeepResearch?: (question: string) => void;
  /** 送信処理中かどうか */
  isLoading?: boolean;
  /** Deep Research実行中かどうか */
  isDeepResearching?: boolean;
  /** プレースホルダーテキスト */
  placeholder?: string;
  /** 最大文字数 */
  maxLength?: number;
}

export default function InputForm({
  onSubmit,
  onDeepResearch,
  isLoading = false,
  isDeepResearching = false,
  placeholder = "メッセージを入力してください...",
  maxLength = 1000,
}: InputFormProps) {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [isDeepResearchMode, setIsDeepResearchMode] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // フォーム送信処理
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    submitMessage();
  };

  // メッセージ送信
  const submitMessage = () => {
    const trimmedInput = input.trim();

    // バリデーション
    if (!trimmedInput) {
      setError("メッセージを入力してください");
      return;
    }

    if (trimmedInput.length > maxLength) {
      setError(`メッセージは${maxLength}文字以内で入力してください`);
      return;
    }

    // エラークリア
    setError("");

    // Deep Research モードかどうかで送信先を分ける
    if (isDeepResearchMode && onDeepResearch) {
      onDeepResearch(trimmedInput);
    } else {
      onSubmit(trimmedInput);
    }

    setInput("");

    // フォーカスを戻す
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  // Deep Research トグル
  const toggleDeepResearch = () => {
    setIsDeepResearchMode(!isDeepResearchMode);
  };

  // 入力変更処理
  const handleInputChange = (value: string) => {
    setInput(value);
    if (error) {
      setError(""); // エラーをクリア
    }
  };

  return (
    <div className="border-t bg-white p-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-2">
        {/* エラーメッセージ */}
        {error && (
          <div className="text-sm text-red-600 px-2" data-testid="input-error">
            {error}
          </div>
        )}

        {/* 入力フィールドとボタン */}
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => handleInputChange(e.target.value)}
            placeholder={placeholder}
            disabled={isLoading || isDeepResearching}
            className="flex-1 min-h-[60px] max-h-[120px] resize-none"
            data-testid="message-input"
          />

          {/* Deep Research トグルボタン */}
          {onDeepResearch && (
            <Button
              type="button"
              onClick={toggleDeepResearch}
              disabled={isLoading || isDeepResearching}
              variant="outline"
              className={`self-end px-3 ${
                isDeepResearchMode
                  ? "bg-blue-500 text-white border-blue-500 hover:bg-blue-600"
                  : "text-gray-400 hover:text-gray-600"
              }`}
              title={`Deep Research ${isDeepResearchMode ? "ON" : "OFF"} - 詳細な調査レポートを生成`}
              data-testid="deep-research-toggle"
            >
              <Search className="h-4 w-4" />
            </Button>
          )}

          {/* 送信ボタン */}
          <Button
            type="submit"
            disabled={isLoading || isDeepResearching || !input.trim()}
            className="self-end px-3"
            data-testid="send-button"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* 文字数カウンターとステータス */}
        <div className="flex justify-between text-xs text-gray-500">
          <span>
            {isLoading
              ? "送信中..."
              : isDeepResearching
                ? "Deep Research実行中..."
                : isDeepResearchMode
                  ? "Deep Research モード - クリックで送信"
                  : "クリックで送信"}
          </span>
          <span>
            {input.length}/{maxLength}
          </span>
        </div>
      </form>
    </div>
  );
}
