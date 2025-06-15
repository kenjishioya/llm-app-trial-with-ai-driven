import { render, screen } from "@testing-library/react";
import { MockedProvider } from "@apollo/client/testing";
import { describe, it, expect, vi } from "vitest";
import AppLayout from "@/components/layout/AppLayout";
import { SessionProvider } from "@/components/providers/SessionProvider";

// Next.js router のモック
vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
    back: vi.fn(),
    forward: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

// SessionProvider のモック
vi.mock("@/components/providers/SessionProvider", () => ({
  SessionProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="session-provider">{children}</div>
  ),
  useSession: () => ({
    currentSession: null,
    sessions: [],
    createSession: vi.fn(),
    deleteSession: vi.fn(),
    updateSessionTitle: vi.fn(),
    setCurrentSession: vi.fn(),
    loading: false,
    error: null,
  }),
}));

// Sidebar のモック
vi.mock("@/components/layout/Sidebar", () => ({
  default: () => <div data-testid="sidebar">Sidebar</div>,
}));

describe("AppLayout", () => {
  const renderAppLayout = (
    children: React.ReactNode = <div>Test Content</div>,
  ) => {
    return render(
      <MockedProvider mocks={[]}>
        <SessionProvider>
          <AppLayout>{children}</AppLayout>
        </SessionProvider>
      </MockedProvider>,
    );
  };

  it("正しくレンダリングされる", () => {
    renderAppLayout();

    expect(screen.getByTestId("session-provider")).toBeInTheDocument();
    expect(screen.getByTestId("sidebar")).toBeInTheDocument();
  });

  it("子コンポーネントが表示される", () => {
    renderAppLayout(<div data-testid="test-child">Test Child Component</div>);

    expect(screen.getByTestId("test-child")).toBeInTheDocument();
    expect(screen.getByText("Test Child Component")).toBeInTheDocument();
  });

  it("サイドバーとメインコンテンツが両方表示される", () => {
    renderAppLayout(<main data-testid="main-content">Main Content</main>);

    expect(screen.getByTestId("sidebar")).toBeInTheDocument();
    expect(screen.getByTestId("main-content")).toBeInTheDocument();
  });

  it("適切なレイアウト構造を持つ", () => {
    const { container } = renderAppLayout();

    // レイアウトの基本構造が存在することを確認
    expect(container.firstChild).toBeInTheDocument();
  });

  it("複数の子要素を処理できる", () => {
    renderAppLayout(
      <>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
      </>,
    );

    expect(screen.getByTestId("child-1")).toBeInTheDocument();
    expect(screen.getByTestId("child-2")).toBeInTheDocument();
  });

  it("SessionProviderが正しくラップされている", () => {
    renderAppLayout();

    expect(screen.getByTestId("session-provider")).toBeInTheDocument();
  });
});
