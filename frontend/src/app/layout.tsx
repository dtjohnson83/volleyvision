import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VolleyVision — Volleyball Video Analytics",
  description: "AI-powered volleyball video analysis: player tracking, ball trajectory, rally detection, and more.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2">
              <span className="text-2xl">🏐</span>
              <span className="text-xl font-bold bg-gradient-to-r from-volleyball-400 to-volleyball-600 bg-clip-text text-transparent">
                VolleyVision
              </span>
            </a>
            <div className="flex gap-4 text-sm text-gray-400">
              <a href="/" className="hover:text-white transition">Upload</a>
              <a href="/results" className="hover:text-white transition">Results</a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
