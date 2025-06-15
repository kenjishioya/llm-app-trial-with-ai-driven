import "@testing-library/jest-dom";

// React 開発ビルドを強制
(process.env as any).NODE_ENV = "test";

// React のビルドモードを確認
console.log("React build mode:", process.env.NODE_ENV);
console.log("React version:", require("react").version);

// EventSource のモック (SSE テスト用)
global.EventSource = class MockEventSource {
  addEventListener = () => {};
  removeEventListener = () => {};
  close = () => {};
  readyState = 1; // OPEN
  constructor(_url: string) {
    // Mock implementation
  }
} as any;

// Reactのact警告を無効化
const originalConsoleError = console.error;
console.error = (...args: any[]) => {
  if (
    typeof args[0] === "string" &&
    args[0].includes("act(...) is not supported")
  ) {
    return;
  }
  originalConsoleError.apply(console, args);
};
