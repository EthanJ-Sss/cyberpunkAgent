"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { fetchArtwork, AuthenticatedClient } from "@/lib/api";
import type { Artwork } from "@/types";

const API_KEY_STORAGE = "cybermarket_api_key";

export default function ArtworkDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [artwork, setArtwork] = useState<Artwork | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [buying, setBuying] = useState(false);
  const [buyError, setBuyError] = useState<string | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchArtwork(id);
        setArtwork(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load artwork");
        setArtwork(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const handleBuy = async () => {
    if (!artwork || artwork.status !== "listed") return;
    let apiKey = typeof window !== "undefined" ? localStorage.getItem(API_KEY_STORAGE) : null;
    if (!apiKey && apiKeyInput.trim()) {
      apiKey = apiKeyInput.trim();
      if (typeof window !== "undefined") localStorage.setItem(API_KEY_STORAGE, apiKey);
    }
    if (!apiKey) {
      setBuyError("请先输入 API Key 并登录");
      return;
    }
    setBuying(true);
    setBuyError(null);
    try {
      const client = new AuthenticatedClient(apiKey);
      await client.buyArtwork(artwork.id);
      router.refresh();
      const data = await fetchArtwork(id);
      setArtwork(data);
    } catch (e) {
      setBuyError(e instanceof Error ? e.message : "Purchase failed");
    } finally {
      setBuying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
      </div>
    );
  }

  if (error || !artwork) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12">
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-400">
          {error || "Artwork not found"}
        </div>
        <Link
          href="/"
          className="mt-4 inline-block font-mono text-cyan-400 hover:text-[#00fff5]"
        >
          ← 返回市场大厅
        </Link>
      </div>
    );
  }

  const qualityPct = Math.round((artwork.quality_score ?? 0) * 100);
  const rarityPct = Math.round((artwork.rarity_score ?? 0) * 100);
  const tier = artwork.model_tier_at_creation ?? 1;

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-2 font-mono text-sm text-cyan-400 hover:text-[#00fff5] transition-colors"
      >
        ← 返回市场大厅
      </Link>

      {/* Title - large gradient text */}
      <h1 className="mb-8 font-mono text-4xl font-bold tracking-wider bg-gradient-to-r from-[#00fff5] via-[#ff00ff] to-[#ffd700] bg-clip-text text-transparent drop-shadow-[0_0_20px_rgba(0,255,245,0.3)]">
        {artwork.title}
      </h1>

      {/* Framed description - the "painting" */}
      <section className="mb-10">
        <div className="relative rounded-lg border-2 border-amber-500/40 bg-[#0d0d12] p-8 shadow-[0_0_40px_rgba(255,215,0,0.15)]">
          <div className="absolute inset-2 rounded border border-amber-500/20" />
          <p className="relative whitespace-pre-wrap font-sans text-base leading-relaxed text-[#e0e0e8]">
            {artwork.description}
          </p>
        </div>
      </section>

      {/* Creative concept */}
      <section className="mb-10">
        <h2 className="mb-3 font-mono text-sm uppercase tracking-widest text-cyan-400/80">
          创作理念
        </h2>
        <p className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-4 font-sans text-zinc-300">
          {artwork.creative_concept}
        </p>
      </section>

      {/* Metadata grid */}
      <section className="mb-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-4">
          <p className="font-mono text-xs text-zinc-500">媒介</p>
          <p className="mt-1 font-mono text-cyan-400">{artwork.medium}</p>
        </div>
        <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-4">
          <p className="font-mono text-xs text-zinc-500">模型层级</p>
          <p className="mt-1 font-mono text-cyan-400">T{tier}</p>
        </div>
        <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-4">
          <p className="font-mono text-xs text-zinc-500">质量分</p>
          <p className="mt-1 font-mono text-cyan-400">{qualityPct}%</p>
        </div>
        <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-4">
          <p className="font-mono text-xs text-zinc-500">稀有度</p>
          <p className="mt-1 font-mono text-fuchsia-400">{rarityPct}%</p>
        </div>
        <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-4">
          <p className="font-mono text-xs text-zinc-500">算力消耗</p>
          <p className="mt-1 font-mono text-amber-400">{artwork.compute_cost} CU</p>
        </div>
      </section>

      {/* Skills used */}
      {artwork.skills_used && artwork.skills_used.length > 0 && (
        <section className="mb-10">
          <h2 className="mb-3 font-mono text-sm uppercase tracking-widest text-cyan-400/80">
            使用技能
          </h2>
          <div className="flex flex-wrap gap-2">
            {artwork.skills_used.map((s) => (
              <span
                key={s}
                className="rounded border border-fuchsia-500/30 bg-fuchsia-500/10 px-3 py-1 font-mono text-sm text-fuchsia-400"
              >
                {s}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Status */}
      <section className="mb-10">
        <span
          className={`inline-block rounded px-3 py-1 font-mono text-sm ${
            artwork.status === "listed"
              ? "border border-amber-500/40 bg-amber-500/20 text-amber-400"
              : artwork.status === "sold"
                ? "border border-cyan-500/40 bg-cyan-500/20 text-cyan-400"
                : "border border-zinc-500/40 bg-zinc-500/20 text-zinc-400"
          }`}
        >
          {artwork.status === "draft"
            ? "草稿"
            : artwork.status === "listed"
              ? "在售"
              : artwork.status === "sold"
                ? "已售"
                : artwork.status}
        </span>
      </section>

      {/* Listed price - big and prominent */}
      {artwork.status === "listed" && artwork.listed_price != null && (
        <section className="mb-10">
          <p className="mb-2 font-mono text-sm text-zinc-500">售价</p>
          <p className="font-mono text-5xl font-bold text-[#ffd700] drop-shadow-[0_0_20px_rgba(255,215,0,0.4)]">
            {artwork.listed_price} CU
          </p>

          {/* Buy button + API key input */}
          <div className="mt-6 space-y-4">
            {buyError && (
              <p className="text-sm text-red-400">{buyError}</p>
            )}
            <div className="flex flex-wrap items-center gap-4">
              <input
                type="password"
                placeholder="API Key (若未登录)"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                className="rounded border border-cyan-500/30 bg-[#12121a] px-4 py-2 font-mono text-sm text-cyan-400 placeholder-zinc-500 outline-none focus:border-cyan-500"
              />
              <button
                onClick={handleBuy}
                disabled={buying}
                className="rounded-lg border border-amber-500/50 bg-amber-500/20 px-6 py-2 font-mono font-bold text-[#ffd700] transition-all hover:border-amber-500 hover:bg-amber-500/30 hover:shadow-[0_0_20px_rgba(255,215,0,0.3)] disabled:opacity-50"
              >
                {buying ? "购买中..." : "立即购买"}
              </button>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
