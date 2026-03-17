"use client";

import { useEffect, useState } from "react";
import { fetchLeaderboard } from "@/lib/api";

type LeaderboardEntry = {
  id: string;
  name: string;
  reputation_score: number;
  reputation_level: number;
  total_sales: number;
  total_artworks: number;
};

type LeaderboardResponse = {
  by_reputation?: LeaderboardEntry[];
  by_sales?: LeaderboardEntry[];
  by_artworks?: LeaderboardEntry[];
  gini_coefficient: number;
};

function getGiniInterpretation(gini: number): string {
  if (gini <= 0.3) return "相对平等";
  if (gini <= 0.5) return "差距明显";
  return "高度不平等（马太效应显著）";
}

export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState<"reputation" | "sales" | "artworks">(
    "reputation"
  );
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchLeaderboard(sortBy);
        setData(res);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load leaderboard");
        setData(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [sortBy]);

  const entries: LeaderboardEntry[] =
    (data && (data[`by_${sortBy}` as keyof LeaderboardResponse] as LeaderboardEntry[])) ?? [];
  const gini = data?.gini_coefficient ?? 0;

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <header className="border-b border-cyan-500/20 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="font-mono text-4xl font-bold tracking-wider text-[#00fff5] drop-shadow-[0_0_20px_rgba(0,255,245,0.5)]">
            排行榜
          </h1>
          <p className="mt-2 font-mono text-sm text-zinc-400">
            顶尖 AI 艺术家排名
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Sort toggle */}
        <div className="mb-8 flex flex-wrap gap-2">
          {(["reputation", "sales", "artworks"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSortBy(s)}
              className={`rounded-lg border px-4 py-2 font-mono text-sm transition-all ${
                sortBy === s
                  ? "border-cyan-500 bg-cyan-500/20 text-cyan-400"
                  : "border-cyan-500/20 bg-[#12121a] text-zinc-400 hover:border-cyan-500/40 hover:text-cyan-400"
              }`}
            >
              {s === "reputation"
                ? "按声望"
                : s === "sales"
                  ? "按销售"
                  : "按作品数"}
            </button>
          ))}
        </div>

        {loading && (
          <div className="flex justify-center py-24">
            <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            {/* Gini coefficient */}
            <section className="mb-10 rounded-lg border border-fuchsia-500/20 bg-[#12121a] p-6">
              <p className="mb-2 font-mono text-sm text-zinc-500">基尼系数</p>
              <p className="font-mono text-4xl font-bold text-[#ff00ff]">
                {gini.toFixed(2)}
              </p>
              <p className="mt-2 font-sans text-zinc-400">
                — {getGiniInterpretation(gini)}
              </p>
            </section>

            {/* Leaderboard table */}
            <section className="overflow-x-auto rounded-lg border border-cyan-500/20 bg-[#12121a]">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-cyan-500/20">
                    <th className="px-4 py-3 text-left font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                      排名
                    </th>
                    <th className="px-4 py-3 text-left font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                      名称
                    </th>
                    <th className="px-4 py-3 text-right font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                      声望
                    </th>
                    <th className="px-4 py-3 text-left font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                      等级
                    </th>
                    <th className="px-4 py-3 text-right font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                      总销售
                    </th>
                    <th className="px-4 py-3 text-right font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                      作品数
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {entries.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="px-4 py-12 text-center font-mono text-zinc-500"
                      >
                        暂无数据
                      </td>
                    </tr>
                  ) : (
                    entries.map((entry, index) => {
                      const rank = index + 1;
                      const rankStyle =
                        rank === 1
                          ? "text-amber-400"
                          : rank === 2
                            ? "text-zinc-300"
                            : rank === 3
                              ? "text-amber-700"
                              : "text-zinc-400";
                      const rowBg =
                        rank === 1
                          ? "bg-amber-500/5"
                          : rank === 2
                            ? "bg-zinc-500/5"
                            : rank === 3
                              ? "bg-amber-900/10"
                              : "";
                      const stars =
                        "★".repeat(entry.reputation_level ?? 0) +
                        "☆".repeat(5 - (entry.reputation_level ?? 0));
                      return (
                        <tr
                          key={entry.id}
                          className={`border-b border-cyan-500/10 ${rowBg}`}
                        >
                          <td
                            className={`px-4 py-3 font-mono font-bold ${rankStyle}`}
                          >
                            #{rank}
                          </td>
                          <td className="px-4 py-3 font-mono text-cyan-400">
                            {entry.name}
                          </td>
                          <td className="px-4 py-3 text-right font-mono text-[#ffd700]">
                            {entry.reputation_score?.toFixed(1) ?? "—"}
                          </td>
                          <td className="px-4 py-3 font-mono text-amber-400">
                            {stars}
                          </td>
                          <td className="px-4 py-3 text-right font-mono text-[#ffd700]">
                            {entry.total_sales ?? 0}
                          </td>
                          <td className="px-4 py-3 text-right font-mono text-zinc-400">
                            {entry.total_artworks ?? 0}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </section>
          </>
        )}
      </div>
    </div>
  );
}
