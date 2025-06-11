import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import LoadingSpinner, {
  LoadingMessage,
  DotsSpinner,
} from "@/components/chat/LoadingSpinner";

describe("LoadingSpinner", () => {
  describe("基本機能", () => {
    it("デフォルト設定で表示される", () => {
      render(<LoadingSpinner />);

      const spinner = screen.getByTestId("loading-spinner");
      expect(spinner).toBeInTheDocument();

      // デフォルトのaria-label
      const spinnerElement = spinner.querySelector('[role="status"]');
      expect(spinnerElement).toHaveAttribute("aria-label", "読み込み中");
    });

    it("カスタムtestIdを設定できる", () => {
      const customTestId = "custom-spinner";
      render(<LoadingSpinner testId={customTestId} />);

      expect(screen.getByTestId(customTestId)).toBeInTheDocument();
    });

    it("カスタムクラス名を適用できる", () => {
      const customClass = "my-custom-class";
      render(<LoadingSpinner className={customClass} />);

      const spinner = screen.getByTestId("loading-spinner");
      expect(spinner).toHaveClass(customClass);
    });
  });

  describe("サイズ設定", () => {
    it("smサイズを適用する", () => {
      render(<LoadingSpinner size="sm" />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("h-4", "w-4");
    });

    it("mdサイズを適用する（デフォルト）", () => {
      render(<LoadingSpinner size="md" />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("h-6", "w-6");
    });

    it("lgサイズを適用する", () => {
      render(<LoadingSpinner size="lg" />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("h-8", "w-8");
    });
  });

  describe("色設定", () => {
    it("primaryカラーを適用する（デフォルト）", () => {
      render(<LoadingSpinner color="primary" />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("text-blue-600");
    });

    it("secondaryカラーを適用する", () => {
      render(<LoadingSpinner color="secondary" />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("text-gray-500");
    });

    it("whiteカラーを適用する", () => {
      render(<LoadingSpinner color="white" />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("text-white");
    });
  });

  describe("ラベル機能", () => {
    it("ラベルなしの場合はテキストを表示しない", () => {
      render(<LoadingSpinner />);

      const container = screen.getByTestId("loading-spinner");
      expect(container.querySelector("span")).not.toBeInTheDocument();
    });

    it("ラベルがある場合はテキストを表示する", () => {
      const labelText = "カスタムローディング...";
      render(<LoadingSpinner label={labelText} />);

      expect(screen.getByText(labelText)).toBeInTheDocument();

      // aria-labelにも反映される
      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveAttribute("aria-label", labelText);
    });

    it("ラベルにもカラークラスが適用される", () => {
      const labelText = "テストラベル";
      render(<LoadingSpinner label={labelText} color="secondary" />);

      const labelElement = screen.getByText(labelText);
      expect(labelElement).toHaveClass("text-gray-500");
    });
  });

  describe("アニメーション", () => {
    it("スピンアニメーションクラスが適用される", () => {
      render(<LoadingSpinner />);

      const spinnerElement = screen.getByRole("status");
      expect(spinnerElement).toHaveClass("animate-spin");
      expect(spinnerElement).toHaveClass("rounded-full");
      expect(spinnerElement).toHaveClass("border-2");
      expect(spinnerElement).toHaveClass("border-current");
      expect(spinnerElement).toHaveClass("border-t-transparent");
    });
  });
});

describe("LoadingMessage", () => {
  it("メッセージ形式のローディングスピナーを表示する", () => {
    render(<LoadingMessage />);

    // メッセージローディングのテストID
    const messageLoading = screen.getByTestId("message-loading");
    expect(messageLoading).toBeInTheDocument();

    // ラベルテキスト
    expect(screen.getByText("回答を生成中...")).toBeInTheDocument();

    // メッセージ形式のスタイル確認
    const messageContainer = messageLoading.closest(".bg-gray-100");
    expect(messageContainer).toBeInTheDocument();
    expect(messageContainer).toHaveClass("rounded-lg", "px-4", "py-3");
  });

  it("小さいサイズとセカンダリーカラーが適用される", () => {
    render(<LoadingMessage />);

    const spinnerElement = screen.getByRole("status");
    expect(spinnerElement).toHaveClass("h-4", "w-4"); // sm size
    expect(spinnerElement).toHaveClass("text-gray-500"); // secondary color
  });
});

describe("DotsSpinner", () => {
  it("3つのドットスピナーを表示する", () => {
    render(<DotsSpinner />);

    const dotsContainer = screen.getByTestId("dots-spinner");
    expect(dotsContainer).toBeInTheDocument();

    // 3つのドットが存在することを確認
    const dots = dotsContainer.querySelectorAll("div");
    expect(dots).toHaveLength(3);

    // 各ドットのスタイル確認
    dots.forEach((dot) => {
      expect(dot).toHaveClass(
        "w-2",
        "h-2",
        "bg-current",
        "rounded-full",
        "animate-bounce",
      );
    });
  });

  it("カスタムtestIdを設定できる", () => {
    const customTestId = "custom-dots";
    render(<DotsSpinner testId={customTestId} />);

    expect(screen.getByTestId(customTestId)).toBeInTheDocument();
  });

  it("カスタムクラス名を適用できる", () => {
    const customClass = "my-dots-class";
    render(<DotsSpinner className={customClass} />);

    const dotsContainer = screen.getByTestId("dots-spinner");
    expect(dotsContainer).toHaveClass(customClass);
  });

  it("アニメーション遅延が適用される", () => {
    render(<DotsSpinner />);

    const dotsContainer = screen.getByTestId("dots-spinner");
    const dots = dotsContainer.querySelectorAll("div");

    // 各ドットの遅延設定を確認
    expect(dots[0]).toHaveClass("[animation-delay:-0.3s]");
    expect(dots[1]).toHaveClass("[animation-delay:-0.15s]");
    // 3番目のドットは遅延なし（デフォルト）
    expect(dots[2]).not.toHaveClass(
      "[animation-delay:-0.3s]",
      "[animation-delay:-0.15s]",
    );
  });

  it("基本的なスタイルが適用される", () => {
    render(<DotsSpinner />);

    const dotsContainer = screen.getByTestId("dots-spinner");
    expect(dotsContainer).toHaveClass("flex", "items-center", "space-x-1");
  });
});

describe("統合テスト", () => {
  it("すべてのコンポーネントが組み合わせて使用できる", () => {
    render(
      <div>
        <LoadingSpinner size="lg" color="primary" label="メインローディング" />
        <LoadingMessage />
        <DotsSpinner testId="footer-dots" />
      </div>,
    );

    // 各コンポーネントが正しく表示される
    expect(screen.getByText("メインローディング")).toBeInTheDocument();
    expect(screen.getByText("回答を生成中...")).toBeInTheDocument();
    expect(screen.getByTestId("footer-dots")).toBeInTheDocument();
  });
});
