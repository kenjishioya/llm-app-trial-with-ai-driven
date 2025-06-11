import { describe, it, expect } from "vitest";

describe("Vitest Setup", () => {
  it("基本的なテストが動作する", () => {
    expect(1 + 1).toBe(2);
  });

  it("jest-domの機能が利用できる", () => {
    const div = document.createElement("div");
    div.textContent = "テストコンテンツ";
    document.body.appendChild(div);

    expect(div).toBeInTheDocument();
    expect(div).toHaveTextContent("テストコンテンツ");
  });

  it("EventSourceのモックが動作する", () => {
    const es = new EventSource("http://localhost/test");
    expect(es.readyState).toBe(1); // OPEN
  });
});
