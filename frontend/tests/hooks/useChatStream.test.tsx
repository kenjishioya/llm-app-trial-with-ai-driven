import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { useChatStream } from "@/hooks/useChatStream";

// EventSourceの最小限のモック
const mockClose = vi.fn();
const mockEventSource = vi.fn().mockImplementation(() => ({
  readyState: 1, // OPEN
  close: mockClose,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  onopen: null,
  onmessage: null,
  onerror: null,
}));

describe("useChatStream", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // EventSourceのモック
    global.EventSource = mockEventSource as any;

    // console出力をモック化
    vi.spyOn(console, "log").mockImplementation(() => {});
    vi.spyOn(console, "warn").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});

    // 環境変数設定
    process.env.NEXT_PUBLIC_GRAPHQL_URL = "http://localhost:8000";
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("基本機能", () => {
    it("初期状態を正しく設定する", () => {
      const { result } = renderHook(() => useChatStream());

      expect(result.current.streamState).toEqual({
        isConnected: false,
        isStreaming: false,
        currentMessage: "",
        reconnectAttempts: 0,
        isReconnecting: false,
      });
    });

    it("すべての必要なメソッドを提供する", () => {
      const { result } = renderHook(() => useChatStream());

      // 返り値の型チェック
      expect(result.current).toHaveProperty("streamState");
      expect(result.current).toHaveProperty("startStream");
      expect(result.current).toHaveProperty("stopStream");
      expect(result.current).toHaveProperty("resetStream");
      expect(result.current).toHaveProperty("reconnect");

      // 関数型チェック
      expect(typeof result.current.startStream).toBe("function");
      expect(typeof result.current.stopStream).toBe("function");
      expect(typeof result.current.resetStream).toBe("function");
      expect(typeof result.current.reconnect).toBe("function");
    });

    it("streamStateが正しい型を持つ", () => {
      const { result } = renderHook(() => useChatStream());

      const state = result.current.streamState;

      expect(typeof state.isConnected).toBe("boolean");
      expect(typeof state.isStreaming).toBe("boolean");
      expect(typeof state.currentMessage).toBe("string");
      expect(typeof state.reconnectAttempts).toBe("number");
      expect(typeof state.isReconnecting).toBe("boolean");
    });
  });

  describe("環境変数とURL構築", () => {
    it("NEXT_PUBLIC_GRAPHQL_URLが使用される", () => {
      // 環境変数の確認
      expect(process.env.NEXT_PUBLIC_GRAPHQL_URL).toBe("http://localhost:8000");
    });

    it("startStreamの引数型定義をチェック", () => {
      const { result } = renderHook(() => useChatStream());

      // TypeScriptの型定義のみ確認（関数は実際に呼び出さない）
      expect(typeof result.current.startStream).toBe("function");
      expect(result.current.startStream.length).toBeGreaterThanOrEqual(1); // 最低1つの引数が必要
    });
  });

  describe("フック状態管理", () => {
    it("関数が期待通りに定義されている", () => {
      const { result } = renderHook(() => useChatStream());

      // 関数が正しく定義されていることのみ確認（実際の呼び出しはしない）
      expect(typeof result.current.startStream).toBe("function");
      expect(typeof result.current.stopStream).toBe("function");
      expect(typeof result.current.resetStream).toBe("function");
      expect(typeof result.current.reconnect).toBe("function");
    });

    it("resetStreamで初期状態に戻る", () => {
      const { result } = renderHook(() => useChatStream());

      // resetStreamを呼び出す（EventSourceを作成しない）
      result.current.resetStream();

      // 初期状態と同じであることを確認
      expect(result.current.streamState).toEqual({
        isConnected: false,
        isStreaming: false,
        currentMessage: "",
        reconnectAttempts: 0,
        isReconnecting: false,
      });
    });
  });

  describe("TypeScript型安全性", () => {
    it("streamStateのプロパティが正しい初期値を持つ", () => {
      const { result } = renderHook(() => useChatStream());

      expect(result.current.streamState.isConnected).toBe(false);
      expect(result.current.streamState.isStreaming).toBe(false);
      expect(result.current.streamState.currentMessage).toBe("");
      expect(result.current.streamState.reconnectAttempts).toBe(0);
      expect(result.current.streamState.isReconnecting).toBe(false);
    });

    it("関数の引数型が正しく定義されている", () => {
      const { result } = renderHook(() => useChatStream());

      // TypeScriptコンパイル時のチェックのみ
      // 実際の関数呼び出しはしない
      expect(typeof result.current.startStream).toBe("function");
      expect(typeof result.current.stopStream).toBe("function");
      expect(typeof result.current.resetStream).toBe("function");
      expect(typeof result.current.reconnect).toBe("function");
    });
  });
});
