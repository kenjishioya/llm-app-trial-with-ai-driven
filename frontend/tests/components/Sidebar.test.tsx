import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { MockedProvider } from "@apollo/client/testing";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { SessionType } from "@/generated/graphql";

// Next.js router のモック
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

// Button コンポーネントのモック
vi.mock("@/components/ui/button", () => ({
  Button: ({ children, onClick, className, ...props }: any) => (
    <button onClick={onClick} className={className} {...props}>
      {children}
    </button>
  ),
}));

// lucide-react アイコンのモック
vi.mock("lucide-react", () => ({
  MessageSquare: () => <div data-testid="message-square-icon" />,
  X: () => <div data-testid="x-icon" />,
  Edit2: () => <div data-testid="edit2-icon" />,
  Check: () => <div data-testid="check-icon" />,
}));

const mockPush = vi.fn();
const mockOnSessionSelect = vi.fn();
const mockOnDeleteSession = vi.fn();
const mockOnUpdateSessionTitle = vi.fn();

const mockSessions: SessionType[] = [
  {
    id: "test-session-1",
    title: "Current Session",
    createdAt: "2024-01-01T00:00:00Z",
    messages: [],
  },
  {
    id: "test-session-2",
    title: "Previous Session",
    createdAt: "2024-01-02T00:00:00Z",
    messages: [],
  },
];

const defaultProps = {
  isOpen: true,
  currentSessionId: "test-session-1",
  onSessionSelect: mockOnSessionSelect,
  sessions: mockSessions,
  onDeleteSession: mockOnDeleteSession,
  onUpdateSessionTitle: mockOnUpdateSessionTitle,
};

const renderSidebar = (props = {}) => {
  return render(
    <MockedProvider mocks={[]}>
      <Sidebar {...defaultProps} {...props} />
    </MockedProvider>,
  );
};

describe("Sidebar", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useRouter).mockReturnValue({
      push: mockPush,
      replace: vi.fn(),
      refresh: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      prefetch: vi.fn(),
    } as any);
  });

  it("QRAIロゴが表示される", () => {
    renderSidebar();

    expect(screen.getByText("QRAI")).toBeInTheDocument();
  });

  it("QRAIロゴをクリックするとホームに遷移する", async () => {
    renderSidebar();

    const logo = screen.getByText("QRAI");
    fireEvent.click(logo);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/");
    });
  });

  it("セッション一覧が表示される", () => {
    renderSidebar();

    expect(screen.getByText("Current Session")).toBeInTheDocument();
    expect(screen.getByText("Previous Session")).toBeInTheDocument();
  });

  it("アクティブなセッションがハイライト表示される", () => {
    renderSidebar();

    const activeSessionItem = screen
      .getByText("Current Session")
      .closest(".group");
    expect(activeSessionItem).toHaveClass("bg-blue-50");
  });

  it("セッションをクリックすると切り替えられる", async () => {
    renderSidebar();

    const sessionItem = screen.getByText("Previous Session");
    fireEvent.click(sessionItem);

    await waitFor(() => {
      expect(mockOnSessionSelect).toHaveBeenCalledWith("test-session-2");
    });
  });

  it("セッション削除ボタンが表示される", () => {
    renderSidebar();

    const deleteButtons = screen.getAllByTitle("削除");
    expect(deleteButtons).toHaveLength(2);
  });

  it("セッション削除ボタンをクリックすると削除される", async () => {
    renderSidebar();

    const deleteButtons = screen.getAllByTitle("削除");
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockOnDeleteSession).toHaveBeenCalledWith("test-session-1");
    });
  });

  it("セッションタイトル編集ボタンが表示される", () => {
    renderSidebar();

    const editButtons = screen.getAllByTitle("タイトルを編集");
    expect(editButtons).toHaveLength(2);
  });

  it("セッションタイトル編集ボタンをクリックすると編集モードになる", async () => {
    renderSidebar();

    const editButtons = screen.getAllByTitle("タイトルを編集");
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByDisplayValue("Current Session")).toBeInTheDocument();
    });
  });

  it("Enterキーでタイトル編集を保存できる", async () => {
    renderSidebar();

    const editButtons = screen.getAllByTitle("タイトルを編集");
    fireEvent.click(editButtons[0]);

    const input = await screen.findByDisplayValue("Current Session");
    fireEvent.change(input, { target: { value: "Updated Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(mockOnUpdateSessionTitle).toHaveBeenCalledWith(
        "test-session-1",
        "Updated Title",
      );
    });
  });

  it("Escapeキーで編集をキャンセルできる", async () => {
    renderSidebar();

    const editButtons = screen.getAllByTitle("タイトルを編集");
    fireEvent.click(editButtons[0]);

    const input = await screen.findByDisplayValue("Current Session");
    fireEvent.change(input, { target: { value: "Updated Title" } });
    fireEvent.keyDown(input, { key: "Escape" });

    await waitFor(() => {
      expect(mockOnUpdateSessionTitle).not.toHaveBeenCalled();
      expect(screen.getByText("Current Session")).toBeInTheDocument();
    });
  });

  it("セッションが0個の場合、空の状態を表示する", () => {
    renderSidebar({ sessions: [] });

    expect(screen.getByText("履歴はありません")).toBeInTheDocument();
  });

  it("isOpenがfalseの場合、コンポーネントがレンダリングされない", () => {
    const { container } = renderSidebar({ isOpen: false });

    expect(container.firstChild).toBeNull();
  });

  it("チャット履歴ヘッダーが表示される", () => {
    renderSidebar();

    expect(screen.getByText("チャット履歴")).toBeInTheDocument();
  });
});
