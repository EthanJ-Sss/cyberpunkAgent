"use client";

import { useEffect, useState } from "react";
import {
  fetchSkills,
  AuthenticatedClient,
} from "@/lib/api";
import type { Player, Agent, Skill } from "@/types";

const API_KEY_STORAGE = "cybermarket_api_key";

export default function StudioPage() {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [player, setPlayer] = useState<Player | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Login/Register state
  const [username, setUsername] = useState("");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [registering, setRegistering] = useState(false);
  const [loggingIn, setLoggingIn] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [newApiKey, setNewApiKey] = useState<string | null>(null);

  // Create agent state
  const [newAgentName, setNewAgentName] = useState("");
  const [creatingAgent, setCreatingAgent] = useState(false);

  // Create artwork state
  const [selectedAgentId, setSelectedAgentId] = useState("");
  const [artTitle, setArtTitle] = useState("");
  const [artDescription, setArtDescription] = useState("");
  const [artConcept, setArtConcept] = useState("");
  const [artMedium, setArtMedium] = useState("digital");
  const [artSkillsUsed, setArtSkillsUsed] = useState<string[]>([]);
  const [creatingArtwork, setCreatingArtwork] = useState(false);
  const [createdArtworkId, setCreatedArtworkId] = useState<string | null>(null);
  const [listPrice, setListPrice] = useState("");
  const [listing, setListing] = useState(false);

  // Bind OpenClaw
  const [openclawInput, setOpenclawInput] = useState("");

  useEffect(() => {
    const key = typeof window !== "undefined" ? localStorage.getItem(API_KEY_STORAGE) : null;
    setApiKey(key);
  }, []);

  useEffect(() => {
    async function loadSkills() {
      try {
        const data = await fetchSkills();
        setSkills(Array.isArray(data) ? data : []);
      } catch {
        setSkills([]);
      }
    }
    loadSkills();
  }, []);

  useEffect(() => {
    if (!apiKey) {
      setPlayer(null);
      setAgents([]);
      setLoading(false);
      return;
    }
    const key = apiKey;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const client = new AuthenticatedClient(key);
        const [meData, agentsData] = await Promise.all([
          client.getMe(),
          client.getAgents(),
        ]);
        setPlayer(meData);
        setAgents(Array.isArray(agentsData) ? agentsData : agentsData.agents ?? []);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
        setPlayer(null);
        setAgents([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [apiKey]);

  const handleRegister = async () => {
    if (!username.trim()) return;
    setRegistering(true);
    setAuthError(null);
    setNewApiKey(null);
    try {
      const client = new AuthenticatedClient("");
      const res = await client.register(username.trim());
      const key = (res as { api_key?: string }).api_key;
      if (key) {
        if (typeof window !== "undefined") localStorage.setItem(API_KEY_STORAGE, key);
        setApiKey(key);
        setNewApiKey(key);
      } else {
        setAuthError("注册失败，未返回 API Key");
      }
    } catch (e) {
      setAuthError(e instanceof Error ? e.message : "Registration failed");
    } finally {
      setRegistering(false);
    }
  };

  const handleLogin = async () => {
    if (!apiKeyInput.trim()) return;
    setLoggingIn(true);
    setAuthError(null);
    try {
      const client = new AuthenticatedClient(apiKeyInput.trim());
      await client.getMe();
      if (typeof window !== "undefined") localStorage.setItem(API_KEY_STORAGE, apiKeyInput.trim());
      setApiKey(apiKeyInput.trim());
    } catch (e) {
      setAuthError(e instanceof Error ? e.message : "Invalid API Key");
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = () => {
    if (typeof window !== "undefined") localStorage.removeItem(API_KEY_STORAGE);
    setApiKey(null);
    setPlayer(null);
    setAgents([]);
  };

  const handleCreateAgent = async () => {
    if (!newAgentName.trim() || !apiKey) return;
    setCreatingAgent(true);
    try {
      const client = new AuthenticatedClient(apiKey);
      const agent = await client.createAgent(newAgentName.trim());
      setAgents((prev) => [...prev, agent as Agent]);
      setNewAgentName("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create agent");
    } finally {
      setCreatingAgent(false);
    }
  };

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);
  const agentSkills = selectedAgent?.skills ?? [];

  const handleCreateArtwork = async () => {
    if (!apiKey || !selectedAgentId || !artTitle.trim() || !artConcept.trim()) return;
    if (artDescription.length < 200) {
      setError("描述至少需要 200 个字符");
      return;
    }
    setCreatingArtwork(true);
    setError(null);
    try {
      const client = new AuthenticatedClient(apiKey);
      const created = await client.createArtwork({
        agent_id: selectedAgentId,
        title: artTitle.trim(),
        description: artDescription.trim(),
        creative_concept: artConcept.trim(),
        medium: artMedium,
        skills_used: artSkillsUsed.filter((s) => agentSkills.includes(s)),
      });
      const art = created as { id?: string };
      setCreatedArtworkId(art.id ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create artwork");
    } finally {
      setCreatingArtwork(false);
    }
  };

  const handleListForSale = async () => {
    if (!apiKey || !createdArtworkId || !listPrice.trim()) return;
    const price = parseFloat(listPrice);
    if (isNaN(price) || price <= 0) {
      setError("请输入有效价格");
      return;
    }
    setListing(true);
    setError(null);
    try {
      const client = new AuthenticatedClient(apiKey);
      await client.listForSale(createdArtworkId, price);
      setCreatedArtworkId(null);
      setListPrice("");
      setArtTitle("");
      setArtDescription("");
      setArtConcept("");
      setArtSkillsUsed([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to list");
    } finally {
      setListing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <header className="border-b border-cyan-500/20 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 className="font-mono text-4xl font-bold tracking-wider text-[#00fff5] drop-shadow-[0_0_20px_rgba(0,255,245,0.5)]">
            我的工作室
          </h1>
          <p className="mt-2 font-mono text-sm text-zinc-400">
            管理你的 AI 艺术家与作品
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {!apiKey ? (
          /* Login / Register section */
          <section className="mb-12 max-w-md rounded-lg border border-cyan-500/20 bg-[#12121a] p-6">
            <h2 className="mb-4 font-mono text-lg text-cyan-400">登录 / 注册</h2>
            {authError && (
              <p className="mb-4 text-sm text-red-400">{authError}</p>
            )}
            {newApiKey && (
              <p className="mb-4 text-sm text-green-400">注册成功！已自动登录。</p>
            )}
            <div className="space-y-4">
              <div>
                <label className="mb-1 block font-mono text-xs text-zinc-500">用户名（新用户）</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="输入用户名"
                    className="flex-1 rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                  />
                  <button
                    onClick={handleRegister}
                    disabled={registering}
                    className="rounded border border-cyan-500/50 bg-cyan-500/20 px-4 py-2 font-mono text-sm text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-50"
                  >
                    {registering ? "注册中..." : "注册"}
                  </button>
                </div>
              </div>
              <div>
                <label className="mb-1 block font-mono text-xs text-zinc-500">API Key（已有账号）</label>
                <div className="flex gap-2">
                  <input
                    type="password"
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                    placeholder="输入 API Key"
                    className="flex-1 rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                  />
                  <button
                    onClick={handleLogin}
                    disabled={loggingIn}
                    className="rounded border border-cyan-500/50 bg-cyan-500/20 px-4 py-2 font-mono text-sm text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-50"
                  >
                    {loggingIn ? "登录中..." : "登录"}
                  </button>
                </div>
              </div>
            </div>
          </section>
        ) : (
          <>
            {loading && (
              <div className="flex justify-center py-12">
                <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
              </div>
            )}

            {error && (
              <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-400">
                {error}
              </div>
            )}

            {!loading && player && (
              <>
                {/* Player dashboard */}
                <section className="mb-12">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="rounded-lg border border-cyan-500/20 bg-[#12121a] p-6">
                      <p className="font-mono text-xs text-zinc-500">用户名</p>
                      <p className="mt-1 font-mono text-lg text-cyan-400">{player.username}</p>
                      <p className="mt-2 font-mono text-xs text-zinc-500">余额</p>
                      <p className="mt-1 font-mono text-4xl font-bold text-[#ffd700]">
                        {player.balance} CU
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <input
                        type="text"
                        value={openclawInput}
                        onChange={(e) => setOpenclawInput(e.target.value)}
                        placeholder="Bind OpenClaw 端点"
                        className="rounded border border-cyan-500/30 bg-[#12121a] px-4 py-2 font-mono text-sm text-cyan-400 placeholder-zinc-500 outline-none focus:border-cyan-500"
                      />
                      <button
                        onClick={handleLogout}
                        className="rounded border border-red-500/30 bg-red-500/10 px-4 py-2 font-mono text-sm text-red-400 hover:bg-red-500/20"
                      >
                        退出登录
                      </button>
                    </div>
                  </div>
                </section>

                {/* My Agents */}
                <section className="mb-12">
                  <h2 className="mb-4 font-mono text-xl text-cyan-400">我的艺术家</h2>
                  <div className="mb-4 flex flex-wrap items-center gap-4">
                    <input
                      type="text"
                      value={newAgentName}
                      onChange={(e) => setNewAgentName(e.target.value)}
                      placeholder="新艺术家名称"
                      className="rounded border border-cyan-500/30 bg-[#12121a] px-4 py-2 font-mono text-sm text-cyan-400 placeholder-zinc-500 outline-none focus:border-cyan-500"
                    />
                    <button
                      onClick={handleCreateAgent}
                      disabled={creatingAgent || !newAgentName.trim()}
                      className="rounded border border-cyan-500/50 bg-cyan-500/20 px-4 py-2 font-mono text-sm text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-50"
                    >
                      {creatingAgent ? "创建中..." : "创建新艺术家"}
                    </button>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {agents.map((agent) => (
                      <AgentCard key={agent.id} agent={agent} />
                    ))}
                  </div>
                </section>

                {/* Create Artwork form */}
                <section className="mb-12 rounded-lg border border-cyan-500/20 bg-[#12121a] p-6">
                  <h2 className="mb-6 font-mono text-xl text-cyan-400">创作作品</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="mb-1 block font-mono text-xs text-zinc-500">选择艺术家</label>
                      <select
                        value={selectedAgentId}
                        onChange={(e) => {
                          setSelectedAgentId(e.target.value);
                          setArtSkillsUsed([]);
                        }}
                        className="w-full rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                      >
                        <option value="">-- 选择 --</option>
                        {agents.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.name} (T{a.model_tier})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="mb-1 block font-mono text-xs text-zinc-500">标题</label>
                      <input
                        type="text"
                        value={artTitle}
                        onChange={(e) => setArtTitle(e.target.value)}
                        className="w-full rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                      />
                    </div>
                    <div>
                      <label className="mb-1 block font-mono text-xs text-zinc-500">
                        描述（至少 200 字符）
                      </label>
                      <textarea
                        value={artDescription}
                        onChange={(e) => setArtDescription(e.target.value)}
                        rows={6}
                        className="w-full rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                      />
                      <p className="mt-1 font-mono text-xs text-zinc-500">
                        {artDescription.length}/200 字符
                      </p>
                    </div>
                    <div>
                      <label className="mb-1 block font-mono text-xs text-zinc-500">创作理念</label>
                      <textarea
                        value={artConcept}
                        onChange={(e) => setArtConcept(e.target.value)}
                        rows={3}
                        className="w-full rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                      />
                    </div>
                    <div>
                      <label className="mb-1 block font-mono text-xs text-zinc-500">媒介</label>
                      <select
                        value={artMedium}
                        onChange={(e) => setArtMedium(e.target.value)}
                        className="w-full rounded border border-cyan-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-cyan-400 outline-none focus:border-cyan-500"
                      >
                        <option value="digital">Digital</option>
                        <option value="painting">Painting</option>
                        <option value="sculpture">Sculpture</option>
                        <option value="photography">Photography</option>
                        <option value="mixed">Mixed</option>
                        <option value="sketch">Sketch</option>
                      </select>
                    </div>
                    {selectedAgentId && agentSkills.length > 0 && (
                      <div>
                        <label className="mb-2 block font-mono text-xs text-zinc-500">使用技能（仅显示该艺术家已拥有）</label>
                        <div className="flex flex-wrap gap-2">
                          {agentSkills.map((s) => (
                            <label key={s} className="flex cursor-pointer items-center gap-2">
                              <input
                                type="checkbox"
                                checked={artSkillsUsed.includes(s)}
                                onChange={(e) =>
                                  setArtSkillsUsed((prev) =>
                                    e.target.checked ? [...prev, s] : prev.filter((x) => x !== s)
                                  )
                                }
                                className="rounded border-cyan-500/50"
                              />
                              <span className="font-mono text-sm text-zinc-400">{s}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                    <button
                      onClick={handleCreateArtwork}
                      disabled={
                        creatingArtwork ||
                        !selectedAgentId ||
                        !artTitle.trim() ||
                        !artConcept.trim() ||
                        artDescription.length < 200
                      }
                      className="rounded border border-cyan-500/50 bg-cyan-500/20 px-6 py-2 font-mono text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-50"
                    >
                      {creatingArtwork ? "创建中..." : "提交创作"}
                    </button>
                  </div>

                  {/* List for sale (after creation) */}
                  {createdArtworkId && (
                    <div className="mt-6 rounded border border-amber-500/20 bg-amber-500/5 p-4">
                      <p className="mb-2 font-mono text-sm text-amber-400">作品已创建！是否上架出售？</p>
                      <div className="flex flex-wrap items-center gap-4">
                        <input
                          type="number"
                          value={listPrice}
                          onChange={(e) => setListPrice(e.target.value)}
                          placeholder="售价 (CU)"
                          min="0"
                          step="0.01"
                          className="rounded border border-amber-500/30 bg-[#0a0a0f] px-3 py-2 font-mono text-sm text-amber-400 outline-none focus:border-amber-500"
                        />
                        <button
                          onClick={handleListForSale}
                          disabled={listing || !listPrice.trim()}
                          className="rounded border border-amber-500/50 bg-amber-500/20 px-4 py-2 font-mono text-amber-400 hover:bg-amber-500/30 disabled:opacity-50"
                        >
                          {listing ? "上架中..." : "上架出售"}
                        </button>
                      </div>
                    </div>
                  )}
                </section>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function AgentCard({ agent }: { agent: Agent }) {
  const stars = "★".repeat(agent.reputation_level ?? 0) + "☆".repeat(5 - (agent.reputation_level ?? 0));
  return (
    <div className="rounded-lg border border-cyan-500/20 bg-[#0a0a0f] p-4 transition-all hover:border-cyan-500/40">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-mono font-semibold text-cyan-400">{agent.name}</h3>
        <span className="rounded bg-cyan-500/20 px-2 py-0.5 font-mono text-xs text-cyan-400">
          T{agent.model_tier}
        </span>
      </div>
      <div className="mb-2 flex flex-wrap gap-1">
        {(agent.skills ?? []).slice(0, 5).map((s) => (
          <span
            key={s}
            className="rounded border border-fuchsia-500/30 bg-fuchsia-500/10 px-1.5 py-0.5 font-mono text-xs text-fuchsia-400"
          >
            {s}
          </span>
        ))}
      </div>
      <p className="mb-2 font-mono text-sm text-amber-400">{stars}</p>
      <div className="flex justify-between font-mono text-xs text-zinc-500">
        <span>作品 {agent.total_artworks ?? 0}</span>
        <span>销售 {agent.total_sales ?? 0}</span>
      </div>
    </div>
  );
}
