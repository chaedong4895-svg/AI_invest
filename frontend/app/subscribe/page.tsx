"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function SubscribePage() {
  const [tab, setTab] = useState<"telegram" | "email">("telegram");
  const [contact, setContact] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async () => {
    if (!contact.trim()) return;
    setLoading(true);
    try {
      const res = await api.subscribe(tab, contact.trim());
      setStatus(res.message ?? "완료되었습니다.");
      setContact("");
    } catch {
      setStatus("오류가 발생했습니다. 다시 시도해주세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-10">
      <h1 className="text-2xl font-bold text-slate-900 mb-2">알림 구독</h1>
      <p className="text-slate-500 text-sm mb-8">
        매일 오전 7시에 AI 투자 리포트를 받아보세요.
      </p>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-5">
        <div className="flex gap-2">
          {(["telegram", "email"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition ${
                tab === t
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {t === "telegram" ? "📱 텔레그램" : "📧 이메일"}
            </button>
          ))}
        </div>

        {tab === "telegram" && (
          <div className="bg-blue-50 rounded-xl p-4 text-sm text-blue-700 space-y-1">
            <div className="font-medium">텔레그램 구독 방법</div>
            <div>1. 텔레그램에서 AI 투자 리포트 Bot을 검색하세요.</div>
            <div>2. /start 명령을 입력하면 Chat ID가 발급됩니다.</div>
            <div>3. 발급된 Chat ID를 아래에 입력하세요.</div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            {tab === "telegram" ? "텔레그램 Chat ID" : "이메일 주소"}
          </label>
          <input
            type={tab === "email" ? "email" : "text"}
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            placeholder={tab === "telegram" ? "예: 123456789" : "예: you@example.com"}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          onClick={handleSubscribe}
          disabled={loading || !contact.trim()}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {loading ? "처리 중..." : "구독하기"}
        </button>

        {status && (
          <div className="text-center text-sm text-green-600 font-medium">{status}</div>
        )}
      </div>
    </div>
  );
}
