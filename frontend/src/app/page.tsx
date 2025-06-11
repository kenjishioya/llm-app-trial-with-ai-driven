"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/components/providers/SessionProvider";

export default function HomePage() {
  const router = useRouter();
  const { createSession, isCreating } = useSession();

  const handleStartChat = async () => {
    const session = await createSession("新しいチャット");
    if (session) {
      router.push("/chat");
    }
  };
  return (
    <div className="flex min-h-full flex-col bg-white">
      <main className="flex-1">
        <div className="px-6 py-12 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              QRAI
            </h1>
            <p className="mt-6 text-xl leading-8 text-gray-600">
              AI-Powered Research Assistant
            </p>
            <p className="mt-4 text-lg text-gray-600">
              QRAIは最新のAI技術を活用したリサーチアシスタントです。
              質問に対してRAGと深度調査で正確な回答を提供します。
            </p>

            <div className="mt-10 flex items-center justify-center gap-x-6">
              <button
                onClick={handleStartChat}
                disabled={isCreating}
                className="rounded-md bg-gray-900 px-4 py-3 text-sm font-semibold text-white shadow-sm hover:bg-gray-800 disabled:opacity-50"
              >
                {isCreating ? "作成中..." : "チャットを開始"}
              </button>
              <a
                href="#features"
                className="text-sm font-semibold leading-6 text-gray-900"
              >
                機能について <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>

          {/* 機能紹介セクション */}
          <div id="features" className="mx-auto mt-20 max-w-5xl">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="text-center p-6 rounded-lg border border-gray-200 bg-white shadow-sm">
                <div className="mx-auto h-12 w-12 rounded-lg bg-blue-100 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth="1.5"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"
                    />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  RAG検索
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  知識ベースを活用した高精度な情報検索と回答生成
                </p>
              </div>

              <div className="text-center p-6 rounded-lg border border-gray-200 bg-white shadow-sm">
                <div className="mx-auto h-12 w-12 rounded-lg bg-green-100 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-green-600"
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
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  深度調査
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  複数ソースを活用した詳細なリサーチと分析
                </p>
              </div>

              <div className="text-center p-6 rounded-lg border border-gray-200 bg-white shadow-sm">
                <div className="mx-auto h-12 w-12 rounded-lg bg-purple-100 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-purple-600"
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
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  ストリーミング
                </h3>
                <p className="mt-2 text-sm text-gray-600">
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
