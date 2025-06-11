import "@testing-library/jest-dom";

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
