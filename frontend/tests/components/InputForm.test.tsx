import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import InputForm from "@/components/chat/InputForm";

describe("InputForm", () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  describe("基本機能", () => {
    it("入力フィールドと送信ボタンを表示する", () => {
      render(<InputForm onSubmit={mockOnSubmit} />);

      expect(screen.getByTestId("message-input")).toBeInTheDocument();
      expect(screen.getByTestId("send-button")).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText("メッセージを入力してください..."),
      ).toBeInTheDocument();
    });

    it("メッセージを入力できる", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      await user.type(input, "テストメッセージ");

      expect(input).toHaveValue("テストメッセージ");
    });

    it("プレースホルダーをカスタマイズできる", () => {
      const customPlaceholder = "カスタムプレースホルダー";
      render(
        <InputForm onSubmit={mockOnSubmit} placeholder={customPlaceholder} />,
      );

      expect(
        screen.getByPlaceholderText(customPlaceholder),
      ).toBeInTheDocument();
    });
  });

  describe("送信機能", () => {
    it("送信ボタンクリックでメッセージを送信する", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      const sendButton = screen.getByTestId("send-button");

      await user.type(input, "テストメッセージ");
      await user.click(sendButton);

      expect(mockOnSubmit).toHaveBeenCalledWith("テストメッセージ");
      expect(input).toHaveValue(""); // 送信後にクリア
    });

    it("Enterキーで送信する", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      await user.type(input, "Enterキーテスト");
      await user.keyboard("{Enter}");

      expect(mockOnSubmit).toHaveBeenCalledWith("Enterキーテスト");
      expect(input).toHaveValue("");
    });

    it("Shift+Enterで改行する（送信しない）", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      await user.type(input, "1行目");
      await user.keyboard("{Shift>}{Enter}{/Shift}");
      await user.type(input, "2行目");

      expect(mockOnSubmit).not.toHaveBeenCalled();
      expect(input).toHaveValue("1行目\n2行目");
    });

    it("前後の空白を削除して送信する", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      await user.type(input, "  前後に空白があるメッセージ  ");
      await user.click(screen.getByTestId("send-button"));

      expect(mockOnSubmit).toHaveBeenCalledWith("前後に空白があるメッセージ");
    });
  });

  describe("バリデーション", () => {
    it("空文字は送信できない", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const sendButton = screen.getByTestId("send-button");
      expect(sendButton).toBeDisabled();

      await user.click(sendButton);
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("空白のみの場合は送信ボタンが無効化される", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      const sendButton = screen.getByTestId("send-button");

      await user.type(input, "   ");

      // 空白のみの場合は送信ボタンが無効化される
      expect(sendButton).toBeDisabled();
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("最大文字数を超えた場合にエラーメッセージを表示", async () => {
      const user = userEvent.setup();
      const maxLength = 10;
      render(<InputForm onSubmit={mockOnSubmit} maxLength={maxLength} />);

      const input = screen.getByTestId("message-input");
      const longMessage = "a".repeat(maxLength + 1);

      await user.type(input, longMessage);
      await user.click(screen.getByTestId("send-button"));

      expect(screen.getByTestId("input-error")).toHaveTextContent(
        `メッセージは${maxLength}文字以内で入力してください`,
      );
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("エラー状態でも入力を続けるとエラーがクリアされる", async () => {
      const user = userEvent.setup();
      const maxLength = 5;
      render(<InputForm onSubmit={mockOnSubmit} maxLength={maxLength} />);

      const input = screen.getByTestId("message-input");

      // 文字数超過でエラーを発生させる
      const longMessage = "a".repeat(maxLength + 1);
      await user.type(input, longMessage);
      await user.click(screen.getByTestId("send-button"));
      expect(screen.getByTestId("input-error")).toBeInTheDocument();

      // 有効な入力をするとエラーがクリア
      await user.clear(input);
      await user.type(input, "OK");
      expect(screen.queryByTestId("input-error")).not.toBeInTheDocument();
    });
  });

  describe("ローディング状態", () => {
    it("ローディング中は入力と送信ボタンが無効化される", () => {
      render(<InputForm onSubmit={mockOnSubmit} isLoading={true} />);

      const input = screen.getByTestId("message-input");
      const sendButton = screen.getByTestId("send-button");

      expect(input).toBeDisabled();
      expect(sendButton).toBeDisabled();
    });

    it("ローディング中はEnterキーでの送信が無効化される", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} isLoading={true} />);

      const input = screen.getByTestId("message-input");

      // disabledの場合はuserEvent.typeが動作しないため、直接値を設定
      fireEvent.change(input, { target: { value: "テストメッセージ" } });
      await user.keyboard("{Enter}");

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("ローディング中はヘルプテキストが変更される", () => {
      render(<InputForm onSubmit={mockOnSubmit} isLoading={true} />);

      expect(screen.getByText("送信中...")).toBeInTheDocument();
    });
  });

  describe("文字数カウンター", () => {
    it("文字数カウンターを表示する", async () => {
      const user = userEvent.setup();
      const maxLength = 100;
      render(<InputForm onSubmit={mockOnSubmit} maxLength={maxLength} />);

      expect(screen.getByText(`0/${maxLength}`)).toBeInTheDocument();

      const input = screen.getByTestId("message-input");
      await user.type(input, "テスト");

      expect(screen.getByText(`3/${maxLength}`)).toBeInTheDocument();
    });

    it("ヘルプテキストを表示する", () => {
      render(<InputForm onSubmit={mockOnSubmit} />);

      expect(
        screen.getByText("Enter で送信、Shift+Enter で改行"),
      ).toBeInTheDocument();
    });
  });

  describe("UI状態", () => {
    it("入力がある場合のみ送信ボタンが有効化される", async () => {
      const user = userEvent.setup();
      render(<InputForm onSubmit={mockOnSubmit} />);

      const input = screen.getByTestId("message-input");
      const sendButton = screen.getByTestId("send-button");

      // 初期状態では無効
      expect(sendButton).toBeDisabled();

      // 入力があると有効化
      await user.type(input, "a");
      expect(sendButton).toBeEnabled();

      // 空白のみでは無効
      await user.clear(input);
      await user.type(input, "   ");
      expect(sendButton).toBeDisabled();
    });

    it("送信ボタンにSendアイコンが表示される", () => {
      render(<InputForm onSubmit={mockOnSubmit} />);

      const sendButton = screen.getByTestId("send-button");
      expect(sendButton.querySelector("svg")).toBeInTheDocument();
    });
  });
});
