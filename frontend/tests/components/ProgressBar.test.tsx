import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import ProgressBar from "@/components/chat/ProgressBar";

describe("ProgressBar", () => {
  it("基本的な進捗情報が表示される", () => {
    render(
      <ProgressBar
        progress={33}
        currentNode="retrieve"
        messages={["Searching for information..."]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("Deep Research")).toBeInTheDocument();
    expect(screen.getByText("検索中")).toBeInTheDocument();
    expect(screen.getByText("33%")).toBeInTheDocument();
  });

  it("進捗メッセージが表示される", () => {
    render(
      <ProgressBar
        progress={50}
        currentNode="decide"
        messages={["Message 1", "Message 2", "Current message"]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("Current message")).toBeInTheDocument();
  });

  it("異なるノードで適切なアイコンと色が使用される", () => {
    const { rerender } = render(
      <ProgressBar
        progress={25}
        currentNode="retrieve"
        messages={["Retrieving..."]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("検索中")).toBeInTheDocument();

    rerender(
      <ProgressBar
        progress={50}
        currentNode="decide"
        messages={["Deciding..."]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("判定中")).toBeInTheDocument();

    rerender(
      <ProgressBar
        progress={90}
        currentNode="answer"
        messages={["Generating..."]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("レポート生成")).toBeInTheDocument();
  });

  it("0%の進捗が正しく表示される", () => {
    render(
      <ProgressBar
        progress={0}
        currentNode="start"
        messages={["Starting..."]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("100%の進捗が正しく表示される", () => {
    render(
      <ProgressBar
        progress={100}
        currentNode="complete"
        messages={["Complete!"]}
        isComplete={true}
      />,
    );

    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText("完了")).toBeInTheDocument();
  });

  it("エラー状態が正しく表示される", () => {
    render(
      <ProgressBar
        progress={30}
        currentNode="error"
        messages={["Error occurred"]}
        error="Connection failed"
        isComplete={false}
      />,
    );

    expect(screen.getByText("エラーが発生しました")).toBeInTheDocument();
    expect(screen.getByText("Connection failed")).toBeInTheDocument();
  });

  it("完了状態でメッセージが表示される", () => {
    render(
      <ProgressBar
        progress={100}
        currentNode="complete"
        messages={["Research completed"]}
        isComplete={true}
      />,
    );

    expect(
      screen.getByText("Deep Research が完了しました"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("詳細なレポートが生成されました。"),
    ).toBeInTheDocument();
  });

  it("複数のメッセージが表示される（最新5件まで）", () => {
    const messages = [
      "Message 1",
      "Message 2",
      "Message 3",
      "Message 4",
      "Message 5",
      "Message 6", // 最新のメッセージ
    ];

    render(
      <ProgressBar
        progress={80}
        currentNode="answer"
        messages={messages}
        isComplete={false}
      />,
    );

    // 最新の5件が表示される
    expect(screen.getByText("Message 6")).toBeInTheDocument();
    expect(screen.getByText("Message 2")).toBeInTheDocument();
    // 最古のメッセージは表示されない
    expect(screen.queryByText("Message 1")).not.toBeInTheDocument();
  });

  it("ステップ進捗が正しく表示される", () => {
    render(
      <ProgressBar
        progress={60}
        currentNode="decide"
        messages={["Deciding..."]}
        isComplete={false}
      />,
    );

    expect(screen.getByText("検索")).toBeInTheDocument();
    expect(screen.getByText("判定")).toBeInTheDocument();
    expect(screen.getByText("レポート")).toBeInTheDocument();
  });

  it("エラーと完了が同時の場合、エラーが優先表示される", () => {
    render(
      <ProgressBar
        progress={100}
        currentNode="error"
        messages={["Error after completion"]}
        error="Final error"
        isComplete={true}
      />,
    );

    expect(screen.getByText("エラーが発生しました")).toBeInTheDocument();
    expect(screen.getByText("Final error")).toBeInTheDocument();
    // 完了メッセージは表示されない
    expect(
      screen.queryByText("Deep Research が完了しました"),
    ).not.toBeInTheDocument();
  });
});
