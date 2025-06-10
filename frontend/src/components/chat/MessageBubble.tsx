import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  /** メッセージ内容 */
  content: string;
  /** メッセージタイプ - ユーザーかAIか */
  role: "user" | "assistant";
  /** 引用情報（AIメッセージのみ） */
  citations?: string[];
  /** ストリーミング中かどうか */
  isStreaming?: boolean;
  /** メッセージID（テスト用） */
  messageId?: string;
}

export default function MessageBubble({
  content,
  role,
  citations = [],
  isStreaming = false,
  messageId,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start",
      )}
      data-testid={`message-${role}-${messageId || "unknown"}`}
    >
      <div
        className={cn(
          "max-w-[80%] px-4 py-3 rounded-lg",
          isUser
            ? "bg-blue-600 text-white ml-4"
            : "bg-gray-100 text-gray-900 mr-4",
          isStreaming && "animate-pulse",
        )}
      >
        {/* メッセージ本文 */}
        <div className="whitespace-pre-wrap break-words">
          {content}
          {isStreaming && (
            <span className="inline-block w-2 h-5 ml-1 bg-current animate-pulse" />
          )}
        </div>

        {/* 引用リンク（AIメッセージのみ） */}
        {!isUser && citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-500 mb-2">参考資料:</div>
            <div className="flex flex-wrap gap-2">
              {citations.map((citation, index) => (
                <a
                  key={index}
                  href={citation}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-2 py-1 text-xs bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                  data-testid={`citation-${index}`}
                >
                  [{index + 1}]
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
