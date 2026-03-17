import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CyberMarket | AI Art Marketplace",
  description: "Trade AI-generated artworks in the cyberpunk marketplace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased bg-[#0a0a0f] text-[#e0e0e8] min-h-screen`}
      >
        <nav className="sticky top-0 z-50 border-b border-cyan-500/20 bg-[#0a0a0f]/95 backdrop-blur-md cyber-glow-cyan">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              <Link
                href="/"
                className="font-mono text-xl font-bold tracking-wider text-[#00fff5] hover:text-[#00fff5]/90 transition-colors"
              >
                CyberMarket
              </Link>
              <div className="flex items-center gap-6">
                <Link
                  href="/"
                  className="font-mono text-sm text-cyan-400 hover:text-[#00fff5] transition-colors border-b-2 border-transparent hover:border-cyan-500"
                >
                  市场大厅
                </Link>
                <Link
                  href="/studio"
                  className="font-mono text-sm text-zinc-400 hover:text-cyan-400 transition-colors"
                >
                  我的工作室
                </Link>
                <Link
                  href="/skills"
                  className="font-mono text-sm text-zinc-400 hover:text-cyan-400 transition-colors"
                >
                  技能商店
                </Link>
                <Link
                  href="/leaderboard"
                  className="font-mono text-sm text-zinc-400 hover:text-cyan-400 transition-colors"
                >
                  排行榜
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-[calc(100vh-4rem)]">{children}</main>
      </body>
    </html>
  );
}
