"use client";

import { useState, useRef, FormEvent, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";

interface InputFormProps {
  /** メッセージ送信コールバック */
  onSubmit: (message: string) => void;
  /** 送信処理中かどうか */
  isLoading?: boolean;
  /** プレースホルダーテキスト */
  placeholder?: string;
  /** 最大文字数 */
  maxLength?: number;
}

export default function InputForm({
  onSubmit,
  isLoading = false,
  placeholder = "メッセージを入力してください...",
  maxLength = 1000,
}: InputFormProps) {
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
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

    // 送信処理
    onSubmit(trimmedInput);
    setInput("");

    // フォーカスを戻す
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  // キーボードショートカット処理
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter キーで送信（Shift+Enter は改行）
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading) {
        submitMessage();
      }
    }
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

        {/* 入力フィールドと送信ボタン */}
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            className="flex-1 min-h-[60px] max-h-[120px] resize-none"
            data-testid="message-input"
          />
          <Button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="self-end px-3"
            data-testid="send-button"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>

        {/* 文字数カウンター */}
        <div className="flex justify-between text-xs text-gray-500">
          <span>
            {isLoading ? "送信中..." : "Enter で送信、Shift+Enter で改行"}
          </span>
          <span>
            {input.length}/{maxLength}
          </span>
        </div>
      </form>
    </div>
  );
}
