import { render, screen, waitFor } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  SessionProvider,
  useSession,
} from "@/components/providers/SessionProvider";

// GraphQL モック
vi.mock("@/generated/graphql", () => ({
  useGetSessionsQuery: () => ({
    data: null,
    loading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useCreateSessionMutation: () => [vi.fn()],
  useDeleteSessionMutation: () => [vi.fn()],
  useUpdateSessionTitleMutation: () => [vi.fn()],
  useGetSessionQuery: () => ({
    data: null,
    loading: false,
    error: null,
  }),
}));

// useChatSession フックのモック
vi.mock("@/hooks/useChatSession", () => ({
  useChatSession: () => ({
    sessions: [],
    currentSession: null,
    loading: false,
    error: null,
    isCreating: false,
    createSession: vi.fn(),
    selectSession: vi.fn(),
    deleteSession: vi.fn(),
    updateSessionTitle: vi.fn(),
  }),
}));

describe("SessionProvider", () => {
  const TestComponent = () => {
    const context = useSession();
    return (
      <div>
        <div data-testid="sessions-count">{context.sessions.length}</div>
        <div data-testid="current-session">
          {context.currentSession?.id || "none"}
        </div>
        <div data-testid="is-creating">{context.isCreating.toString()}</div>
      </div>
    );
  };

  const renderWithProvider = () => {
    return render(
      <MockedProvider mocks={[]}>
        <SessionProvider>
          <TestComponent />
        </SessionProvider>
      </MockedProvider>,
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("初期状態が正しく設定される", () => {
    renderWithProvider();

    expect(screen.getByTestId("sessions-count")).toHaveTextContent("0");
    expect(screen.getByTestId("current-session")).toHaveTextContent("none");
    expect(screen.getByTestId("is-creating")).toHaveTextContent("false");
  });

  it("子コンポーネントが正しくレンダリングされる", () => {
    renderWithProvider();

    expect(screen.getByTestId("sessions-count")).toBeInTheDocument();
    expect(screen.getByTestId("current-session")).toBeInTheDocument();
    expect(screen.getByTestId("is-creating")).toBeInTheDocument();
  });

  it("useSessionフックがコンテキスト値を返す", () => {
    renderWithProvider();

    // コンテキスト値が正しく提供されることを確認
    expect(screen.getByTestId("sessions-count")).toBeInTheDocument();
    expect(screen.getByTestId("current-session")).toBeInTheDocument();
  });

  it("複数の子コンポーネントが同じコンテキストを共有する", () => {
    const TestComponent1 = () => {
      const { sessions } = useSession();
      return <div data-testid="test-1">{sessions.length}</div>;
    };

    const TestComponent2 = () => {
      const { sessions } = useSession();
      return <div data-testid="test-2">{sessions.length}</div>;
    };

    render(
      <MockedProvider mocks={[]}>
        <SessionProvider>
          <TestComponent1 />
          <TestComponent2 />
        </SessionProvider>
      </MockedProvider>,
    );

    expect(screen.getByTestId("test-1")).toHaveTextContent("0");
    expect(screen.getByTestId("test-2")).toHaveTextContent("0");
  });

  it("プロバイダー外でuseSessionを使用するとエラーになる", () => {
    // コンソールエラーを一時的に抑制
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow("useSession must be used within a SessionProvider");

    consoleSpy.mockRestore();
  });
});
