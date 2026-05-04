import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 투자 리포트",
  description: "매일 아침 AI가 분석한 투자 리포트",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-white text-slate-900">
        <header className="border-b border-slate-100">
          <div className="max-w-4xl mx-auto px-5 h-12 flex items-center justify-between">
            <a href="/" className="font-semibold text-slate-900 tracking-tight">
              AI 투자 리포트
            </a>
            <nav className="flex items-center gap-5 text-sm text-slate-500">
              <a href="/archive" className="hover:text-slate-900 transition-colors">아카이브</a>
              <a href="/subscribe" className="hover:text-slate-900 transition-colors">구독</a>
            </nav>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-5 py-8">{children}</main>

        <footer className="border-t border-slate-100 mt-16 py-5 text-center text-xs text-slate-400">
          투자 결과에 대한 책임은 사용자 본인에게 있습니다.
        </footer>
      </body>
    </html>
  );
}
