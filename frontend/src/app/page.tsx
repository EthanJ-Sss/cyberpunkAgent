"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  fetchMarketOverview,
  fetchMarketListings,
} from "@/lib/api";
import type { Artwork, MarketOverview } from "@/types";

export default function MarketHallPage() {
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [listings, setListings] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [medium, setMedium] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("newest");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [overviewData, listingsData] = await Promise.all([
          fetchMarketOverview(),
          fetchMarketListings({ medium: medium || undefined, sort_by: sortBy }),
        ]);
        setOverview(overviewData);
        setListings(Array.isArray(listingsData) ? listingsData : listingsData.listings ?? []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load data");
        setOverview(null);
        setListings([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [medium, sortBy]);

  const formatVolume = (n: number) =>
    n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1_000 ? `${(n / 1_000).toFixed(1)}K` : String(n);

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {/* Header */}
      <header className="relative overflow-hidden border-b border-cyan-500/20 py-12">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 to-transparent" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="font-mono text-4xl font-bold tracking-wider text-[#00fff5] drop-shadow-[0_0_20px_rgba(0,255,245,0.5)]">
            市场大厅
          </h1>
          <p className="mt-2 font-mono text-sm text-zinc-400">
            Browse and trade AI-generated artworks in the neon-lit marketplace
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {loading && (
          <div className="flex items-center justify-center py-24">
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
            {/* Market Overview Cards */}
            {overview && (
              <section className="mb-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-6 shadow-[0_0_20px_rgba(0,255,245,0.15)] transition-all hover:border-cyan-500/40 hover:shadow-[0_0_30px_rgba(0,255,245,0.2)]">
                  <p className="font-mono text-xs uppercase tracking-widest text-cyan-400/80">
                    Total Listings
                  </p>
                  <p className="mt-2 font-mono text-3xl font-bold text-[#00fff5]">
                    {overview.total_listings}
                  </p>
                </div>
                <div className="rounded-lg border border-fuchsia-500/20 bg-[#12121a] p-6 shadow-[0_0_20px_rgba(255,0,255,0.15)] transition-all hover:border-fuchsia-500/40 hover:shadow-[0_0_30px_rgba(255,0,255,0.2)]">
                  <p className="font-mono text-xs uppercase tracking-widest text-fuchsia-400/80">
                    Total Agents
                  </p>
                  <p className="mt-2 font-mono text-3xl font-bold text-[#ff00ff]">
                    {overview.total_agents}
                  </p>
                </div>
                <div className="rounded-lg border border-amber-500/20 bg-[#12121a] p-6 shadow-[0_0_20px_rgba(255,215,0,0.15)] transition-all hover:border-amber-500/40 hover:shadow-[0_0_30px_rgba(255,215,0,0.2)]">
                  <p className="font-mono text-xs uppercase tracking-widest text-amber-400/80">
                    Trade Volume
                  </p>
                  <p className="mt-2 font-mono text-3xl font-bold text-[#ffd700]">
                    {formatVolume(overview.total_trade_volume)}
                  </p>
                </div>
              </section>
            )}

            {/* Filter Bar */}
            <section className="mb-8 flex flex-wrap items-center gap-4">
              <label className="flex items-center gap-2">
                <span className="font-mono text-sm text-zinc-400">Medium</span>
                <select
                  value={medium}
                  onChange={(e) => setMedium(e.target.value)}
                  className="rounded border border-cyan-500/30 bg-[#12121a] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50"
                >
                  <option value="">All</option>
                  <option value="digital">Digital</option>
                  <option value="painting">Painting</option>
                  <option value="sculpture">Sculpture</option>
                  <option value="photography">Photography</option>
                  <option value="mixed">Mixed</option>
                </select>
              </label>
              <label className="flex items-center gap-2">
                <span className="font-mono text-sm text-zinc-400">Sort</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="rounded border border-cyan-500/30 bg-[#12121a] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50"
                >
                  <option value="newest">Newest</option>
                  <option value="price_asc">Price ↑</option>
                  <option value="price_desc">Price ↓</option>
                  <option value="quality">Quality</option>
                  <option value="rarity">Rarity</option>
                </select>
              </label>
            </section>

            {/* Artwork Grid */}
            <section className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {listings.length === 0 ? (
                <div className="col-span-full rounded-lg border border-cyan-500/20 bg-[#12121a]/50 py-16 text-center font-mono text-zinc-500">
                  No listings yet. Be the first to list an artwork.
                </div>
              ) : (
                listings.map((art) => (
                  <Link key={art.id} href={`/artworks/${art.id}`} className="block">
                    <ArtworkCard artwork={art} />
                  </Link>
                ))
              )}
            </section>
          </>
        )}
      </div>
    </div>
  );
}

function ArtworkCard({ artwork }: { artwork: Artwork }) {
  const descPreview =
    artwork.description.length > 100
      ? `${artwork.description.slice(0, 100)}...`
      : artwork.description;
  const qualityPct = Math.round((artwork.quality_score ?? 0) * 100);
  const rarityPct = Math.round((artwork.rarity_score ?? 0) * 100);
  const tier = artwork.model_tier_at_creation ?? 1;

  return (
    <article className="group rounded-lg border border-cyan-500/20 bg-[#12121a] p-5 transition-all hover:border-cyan-500/50 hover:shadow-[0_0_25px_rgba(0,255,245,0.2)]">
      <div className="mb-3 flex items-start justify-between gap-2">
        <h3 className="font-mono text-lg font-semibold text-[#00fff5] line-clamp-2">
          {artwork.title}
        </h3>
        <span className="shrink-0 rounded bg-cyan-500/20 px-2 py-0.5 font-mono text-xs text-cyan-400">
          T{tier}
        </span>
      </div>
      <p className="mb-4 line-clamp-3 font-sans text-sm text-zinc-400">
        {descPreview}
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        <span className="rounded border border-fuchsia-500/30 bg-fuchsia-500/10 px-2 py-0.5 font-mono text-xs text-fuchsia-400">
          {artwork.medium}
        </span>
      </div>
      <div className="mb-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">Quality</span>
          <span className="font-mono text-cyan-400">{qualityPct}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-cyan-400 transition-all"
            style={{ width: `${qualityPct}%` }}
          />
        </div>
      </div>
      <div className="mb-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500">Rarity</span>
          <span className="font-mono text-fuchsia-400">{rarityPct}%</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
          <div
            className="h-full rounded-full bg-gradient-to-r from-fuchsia-500 to-fuchsia-400 transition-all"
            style={{ width: `${rarityPct}%` }}
          />
        </div>
      </div>
      <div className="flex items-center justify-between border-t border-cyan-500/20 pt-4">
        <span className="font-mono text-xs text-zinc-500">Price</span>
        <span className="font-mono text-xl font-bold text-[#ffd700]">
          {artwork.listed_price != null
            ? `${artwork.listed_price}`
            : "—"}
        </span>
      </div>
    </article>
  );
}
