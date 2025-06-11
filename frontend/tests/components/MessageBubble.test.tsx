import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import MessageBubble from "@/components/chat/MessageBubble";

describe("MessageBubble", () => {
  describe("ユーザーメッセージ", () => {
    it("ユーザーメッセージを正しく表示する", () => {
      render(
        <MessageBubble
          content="テストメッセージ"
          role="user"
          messageId="test-user-1"
        />,
      );

      // メッセージ内容の確認
      expect(screen.getByText("テストメッセージ")).toBeInTheDocument();

      // test-idの確認
      expect(
        screen.getByTestId("message-user-test-user-1"),
      ).toBeInTheDocument();

      // ユーザーメッセージのスタイル確認
      const messageContainer = screen.getByTestId("message-user-test-user-1");
      expect(messageContainer).toHaveClass("justify-end");

      // ユーザーメッセージの背景色確認
      const messageContent = messageContainer.querySelector("div:last-child");
      expect(messageContent).toHaveClass("bg-blue-600", "text-white");
    });

    it("引用リンクは表示されない", () => {
      render(
        <MessageBubble
          content="ユーザーメッセージ"
          role="user"
          citations={["https://example.com"]}
          messageId="test-user-2"
        />,
      );

      // ユーザーメッセージには引用リンクが表示されない
      expect(screen.queryByText("参考資料:")).not.toBeInTheDocument();
      expect(screen.queryByTestId("citation-0")).not.toBeInTheDocument();
    });
  });

  describe("AIアシスタントメッセージ", () => {
    it("AIメッセージを正しく表示する", () => {
      render(
        <MessageBubble
          content="AI応答メッセージ"
          role="assistant"
          messageId="test-ai-1"
        />,
      );

      // メッセージ内容の確認
      expect(screen.getByText("AI応答メッセージ")).toBeInTheDocument();

      // test-idの確認
      expect(
        screen.getByTestId("message-assistant-test-ai-1"),
      ).toBeInTheDocument();

      // AIメッセージのスタイル確認
      const messageContainer = screen.getByTestId(
        "message-assistant-test-ai-1",
      );
      expect(messageContainer).toHaveClass("justify-start");

      // AIメッセージの背景色確認
      const messageContent = messageContainer.querySelector("div:last-child");
      expect(messageContent).toHaveClass("bg-gray-100", "text-gray-900");
    });

    it("引用リンクを正しく表示する", () => {
      const citations = [
        "https://example.com/doc1",
        "https://example.com/doc2",
      ];

      render(
        <MessageBubble
          content="参考資料ありの回答"
          role="assistant"
          citations={citations}
          messageId="test-ai-2"
        />,
      );

      // 参考資料セクションの確認
      expect(screen.getByText("参考資料:")).toBeInTheDocument();

      // 引用リンクの確認
      const citation1 = screen.getByTestId("citation-0");
      expect(citation1).toHaveAttribute("href", "https://example.com/doc1");
      expect(citation1).toHaveAttribute("target", "_blank");
      expect(citation1).toHaveAttribute("rel", "noopener noreferrer");
      expect(citation1).toHaveTextContent("[1]");

      const citation2 = screen.getByTestId("citation-1");
      expect(citation2).toHaveAttribute("href", "https://example.com/doc2");
      expect(citation2).toHaveTextContent("[2]");
    });

    it("引用リンクなしの場合は参考資料セクションを表示しない", () => {
      render(
        <MessageBubble
          content="引用なしの回答"
          role="assistant"
          messageId="test-ai-3"
        />,
      );

      expect(screen.queryByText("参考資料:")).not.toBeInTheDocument();
    });
  });

  describe("ストリーミング状態", () => {
    it("ストリーミング中のユーザーメッセージにアニメーションを表示", () => {
      render(
        <MessageBubble
          content="ストリーミング中メッセージ"
          role="user"
          isStreaming={true}
          messageId="test-streaming-1"
        />,
      );

      const messageContent = screen
        .getByTestId("message-user-test-streaming-1")
        .querySelector("div:last-child");
      expect(messageContent).toHaveClass("animate-pulse");

      // ストリーミングインジケーターの確認
      const streamingIndicator = messageContent?.querySelector("span");
      expect(streamingIndicator).toHaveClass("animate-pulse");
    });

    it("ストリーミング中のAIメッセージにアニメーションを表示", () => {
      render(
        <MessageBubble
          content="AI応答中..."
          role="assistant"
          isStreaming={true}
          messageId="test-streaming-2"
        />,
      );

      const messageContent = screen
        .getByTestId("message-assistant-test-streaming-2")
        .querySelector("div:last-child");
      expect(messageContent).toHaveClass("animate-pulse");
    });

    it("ストリーミング完了時はアニメーションを表示しない", () => {
      render(
        <MessageBubble
          content="完了メッセージ"
          role="assistant"
          isStreaming={false}
          messageId="test-complete-1"
        />,
      );

      const messageContent = screen
        .getByTestId("message-assistant-test-complete-1")
        .querySelector("div:last-child");
      expect(messageContent).not.toHaveClass("animate-pulse");

      // ストリーミングインジケーターがない
      const streamingIndicator = messageContent?.querySelector("span");
      expect(streamingIndicator).toBeNull();
    });
  });

  describe("エッジケース", () => {
    it("messageIdが未指定の場合はunknownを使用", () => {
      render(<MessageBubble content="ID未指定メッセージ" role="user" />);

      expect(screen.getByTestId("message-user-unknown")).toBeInTheDocument();
    });

    it("空の引用配列は参考資料セクションを表示しない", () => {
      render(
        <MessageBubble
          content="空引用配列"
          role="assistant"
          citations={[]}
          messageId="test-empty-citations"
        />,
      );

      expect(screen.queryByText("参考資料:")).not.toBeInTheDocument();
    });

    it("改行を含むメッセージを正しく表示", () => {
      const multilineContent = "1行目\n2行目\n3行目";

      render(
        <MessageBubble
          content={multilineContent}
          role="assistant"
          messageId="test-multiline"
        />,
      );

      // 改行が保持されていることを確認（個別の行を検索）
      expect(screen.getByText(/1行目/)).toBeInTheDocument();
      expect(screen.getByText(/2行目/)).toBeInTheDocument();
      expect(screen.getByText(/3行目/)).toBeInTheDocument();

      // whitespace-pre-wrapクラスが適用されていることを確認
      const messageContent = screen
        .getByTestId("message-assistant-test-multiline")
        .querySelector(".whitespace-pre-wrap");
      expect(messageContent).toBeInTheDocument();
    });
  });
});
