"use client";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { WebSocketProvider } from "./lib/websockets";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="bg-card border-b border-border">
          <div className="max-w-100vh mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-8">
                <Link href="/" className="text-2xl font-bold text-primary hover:text-primary/80 transition-colors">
                  BotArena
                </Link>
                <div className="flex gap-4">
                  <Link
                    href="/game"
                    className="text-foreground hover:text-primary transition-colors font-medium"
                  >
                    Games
                  </Link>
                  <Link
                    href="/leaderboard"
                    className="text-muted-foreground hover:text-primary transition-colors font-medium"
                  >
                    Leaderboard
                  </Link>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button className="text-muted-foreground hover:text-primary transition-colors font-medium">
                  Profile
                </button>
              </div>
            </div>
          </div>
        </nav>
        <WebSocketProvider>
          {children}
        </WebSocketProvider>
      </body>
    </html>
  );
}
