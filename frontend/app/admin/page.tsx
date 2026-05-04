"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState("");
  const [date, setDate] = useState("");
  const [log, setLog] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const call = async (endpoint: string, label: string) => {
    if (!adminKey) { setLog((l) => [`[오류] Admin Key를 입력하세요.`, ...l]); return; }
    setLoading(true);
    const params = date ? `?report_date=${date}` : "";
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/${endpoint}${params}`, {
        method: "POST",
        headers: { "x-admin-key": adminKey },
      });
      const data = await res.json();
      setLog((l) => [`[${new Date().toLocaleTimeString()}] ${label}: ${JSON.stringify(data)}`, ...l]);
    } catch (e) {
      setLog((l) => [`[오류] ${label} 실패: ${e}`, ...l]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-10 space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">관리자 패널</h1>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Admin Key</label>
          <input
            type="password"
            value={adminKey}
            onChange={(e) => setAdminKey(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            날짜 (비워두면 오늘)
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => call("generate", "리포트 생성")}
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            📊 리포트 수동 생성
          </button>
          <button
            onClick={() => call("notify", "알림 발송")}
            disabled={loading}
            className="flex-1 bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50"
          >
            📩 알림 수동 발송
          </button>
        </div>
      </div>

      {log.length > 0 && (
        <div className="bg-slate-900 rounded-xl p-4 text-xs text-green-400 font-mono space-y-1 max-h-64 overflow-y-auto">
          {log.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>
      )}
    </div>
  );
}
