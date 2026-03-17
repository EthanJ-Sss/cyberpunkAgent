"use client";

import { useEffect, useState } from "react";
import { fetchSkills } from "@/lib/api";
import type { Skill } from "@/types";

const TIER_STYLES: Record<
  number,
  { label: string; border: string; bg: string; text: string; accent: string }
> = {
  1: {
    label: "Tier 1 (Basic)",
    border: "border-green-500/30",
    bg: "bg-green-500/5",
    text: "text-green-400",
    accent: "green",
  },
  2: {
    label: "Tier 2 (Professional)",
    border: "border-blue-500/30",
    bg: "bg-blue-500/5",
    text: "text-blue-400",
    accent: "blue",
  },
  3: {
    label: "Tier 3 (Master)",
    border: "border-purple-500/30",
    bg: "bg-purple-500/5",
    text: "text-purple-400",
    accent: "purple",
  },
  4: {
    label: "Tier 4 (Ultimate)",
    border: "border-amber-500/30",
    bg: "bg-amber-500/5",
    text: "text-amber-400",
    accent: "amber",
  },
};

function getTierStyle(tier: number) {
  return TIER_STYLES[tier] ?? TIER_STYLES[1];
}

export default function SkillsShopPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSkills();
        setSkills(Array.isArray(data) ? data : []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load skills");
        setSkills([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const byTier = skills.reduce<Record<number, Skill[]>>((acc, s) => {
    const t = s.tier ?? 1;
    if (!acc[t]) acc[t] = [];
    acc[t].push(s);
    return acc;
  }, {});

  const tiers = Object.keys(byTier)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <header className="border-b border-cyan-500/20 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="font-mono text-4xl font-bold tracking-wider text-[#00fff5] drop-shadow-[0_0_20px_rgba(0,255,245,0.5)]">
            技能商店
          </h1>
          <p className="mt-2 font-mono text-sm text-zinc-400">
            浏览所有可用技能，在工作室中为你的艺术家购买
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
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
          <div className="space-y-12">
            {tiers.map((tier) => {
              const style = getTierStyle(tier);
              const tierSkills = byTier[tier] ?? [];
              return (
                <section key={tier}>
                  <h2
                    className={`mb-6 font-mono text-xl font-semibold ${style.text}`}
                  >
                    {style.label}
                  </h2>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {tierSkills.map((skill) => (
                      <SkillCard key={skill.id} skill={skill} />
                    ))}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function SkillCard({ skill }: { skill: Skill }) {
  const style = getTierStyle(skill.tier ?? 1);
  return (
    <div
      className={`rounded-lg border ${style.border} ${style.bg} p-5 transition-all hover:border-cyan-500/40`}
    >
      <div className="mb-2 flex items-start justify-between gap-2">
        <h3 className={`font-mono font-semibold ${style.text}`}>{skill.name}</h3>
        <span
          className={`shrink-0 rounded px-2 py-0.5 font-mono text-xs ${
            skill.category === "painting"
              ? "border border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
              : skill.category === "sculpture"
                ? "border border-fuchsia-500/30 bg-fuchsia-500/10 text-fuchsia-400"
                : "border border-amber-500/30 bg-amber-500/10 text-amber-400"
          }`}
        >
          {skill.category}
        </span>
      </div>
      <p className="mb-4 font-sans text-sm text-zinc-400">{skill.description}</p>
      {skill.prerequisites && skill.prerequisites.length > 0 && (
        <div className="mb-3">
          <p className="mb-1 font-mono text-xs text-zinc-500">前置技能</p>
          <div className="flex flex-wrap gap-1">
            {skill.prerequisites.map((p) => (
              <span
                key={p}
                className="rounded border border-zinc-500/30 bg-zinc-500/10 px-2 py-0.5 font-mono text-xs text-zinc-400"
              >
                {p}
              </span>
            ))}
          </div>
        </div>
      )}
      <p className="font-mono text-lg font-bold text-[#ffd700]">
        {skill.cost} CU
      </p>
    </div>
  );
}
