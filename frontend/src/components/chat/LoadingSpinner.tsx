import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  /** スピナーのサイズ */
  size?: "sm" | "md" | "lg";
  /** スピナーの色 */
  color?: "primary" | "secondary" | "white";
  /** カスタムクラス名 */
  className?: string;
  /** テスト用ID */
  testId?: string;
  /** ラベルテキスト */
  label?: string;
}

export default function LoadingSpinner({
  size = "md",
  color = "primary",
  className,
  testId = "loading-spinner",
  label,
}: LoadingSpinnerProps) {
  // サイズクラス
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8",
  };

  // 色クラス
  const colorClasses = {
    primary: "text-blue-600",
    secondary: "text-gray-500",
    white: "text-white",
  };

  return (
    <div
      className={cn("flex items-center justify-center", className)}
      data-testid={testId}
    >
      <div className="flex items-center gap-2">
        {/* スピナーアニメーション */}
        <div
          className={cn(
            "animate-spin rounded-full border-2 border-current border-t-transparent",
            sizeClasses[size],
            colorClasses[color],
          )}
          role="status"
          aria-label={label || "読み込み中"}
        />

        {/* ラベル */}
        {label && (
          <span className={cn("text-sm font-medium", colorClasses[color])}>
            {label}
          </span>
        )}
      </div>
    </div>
  );
}

// 使用例コンポーネント
export function LoadingMessage() {
  return (
    <div className="flex justify-start w-full mb-4">
      <div className="max-w-[80%] px-4 py-3 rounded-lg bg-gray-100 text-gray-900 mr-4">
        <LoadingSpinner
          size="sm"
          color="secondary"
          label="回答を生成中..."
          testId="message-loading"
        />
      </div>
    </div>
  );
}

// 3点リーダー型のスピナー
export function DotsSpinner({
  testId = "dots-spinner",
  className,
}: {
  testId?: string;
  className?: string;
}) {
  return (
    <div
      className={cn("flex items-center space-x-1", className)}
      data-testid={testId}
    >
      <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.3s]" />
      <div className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:-0.15s]" />
      <div className="w-2 h-2 bg-current rounded-full animate-bounce" />
    </div>
  );
}
