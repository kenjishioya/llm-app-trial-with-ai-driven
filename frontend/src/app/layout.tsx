import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import ApolloProvider from "@/components/providers/ApolloProvider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "QRAI - AI-Powered Research Assistant",
  description:
    "QRAIは最新のAI技術を活用したリサーチアシスタントです。質問に対してRAGと深度調査で回答します。",
  keywords: ["AI", "research", "assistant", "RAG", "deep research"],
  authors: [{ name: "QRAI Team" }],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className={inter.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ApolloProvider>{children}</ApolloProvider>
      </body>
    </html>
  );
}
