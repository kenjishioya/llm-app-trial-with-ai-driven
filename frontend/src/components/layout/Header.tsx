import React from "react";
import Link from "next/link";

export interface HeaderProps {
  className?: string;
}

export default function Header({ className = "" }: HeaderProps) {
  return (
    <header
      className={`sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 ${className}`}
    >
      <div className="container flex h-14 items-center">
        {/* ロゴ・タイトル */}
        <div className="mr-4 hidden md:flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
              >
                <path d="M9 11H1v3h8v3l3-3.5L9 11z" />
                <path d="M20 12.5a8.5 8.5 0 1 0-9 8.5h9v-8.5z" />
              </svg>
            </div>
            <span className="hidden font-bold sm:inline-block">QRAI</span>
          </Link>
        </div>

        {/* モバイル用ロゴ */}
        <div className="flex md:hidden">
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
              >
                <path d="M9 11H1v3h8v3l3-3.5L9 11z" />
                <path d="M20 12.5a8.5 8.5 0 1 0-9 8.5h9v-8.5z" />
              </svg>
            </div>
            <span className="font-bold">QRAI</span>
          </Link>
        </div>

        {/* ナビゲーション */}
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link
              href="/chat"
              className="transition-colors hover:text-foreground/80 text-foreground"
            >
              チャット
            </Link>
            <Link
              href="/sessions"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              履歴
            </Link>
          </nav>

          {/* ユーザーメニュー（将来の認証機能用） */}
          <div className="flex items-center space-x-2">
            <div className="hidden h-8 w-8 rounded-full bg-muted md:flex items-center justify-center">
              <span className="text-xs font-medium">U</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
