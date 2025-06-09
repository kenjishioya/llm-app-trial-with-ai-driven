import React from "react";
import Link from "next/link";
import Header from "@/components/layout/Header";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">
        <div className="container px-4 py-8">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
              QRAI
            </h1>
            <p className="mt-6 text-lg leading-8 text-muted-foreground">
              AI-Powered Research Assistant
            </p>
            <p className="mt-4 text-base text-muted-foreground">
              QRAIは最新のAI技術を活用したリサーチアシスタントです。
              質問に対してRAGと深度調査で正確な回答を提供します。
            </p>

            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/chat"
                className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                チャットを開始
              </Link>
              <a
                href="#features"
                className="text-sm font-semibold leading-6 text-foreground"
              >
                機能について <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>

          {/* 機能紹介セクション */}
          <div id="features" className="mx-auto mt-16 max-w-4xl">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="text-center">
                <div className="mx-auto h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-primary"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189 6.01 6.01 0 01-.75-1.061"
                    />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-medium">RAG検索</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  知識ベースを活用した高精度な情報検索と回答生成
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-primary"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75"
                    />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-medium">深度調査</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  複数ソースを活用した詳細なリサーチと分析
                </p>
              </div>

              <div className="text-center">
                <div className="mx-auto h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-primary"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155"
                    />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-medium">ストリーミング</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  リアルタイムで段階的に回答を表示
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
