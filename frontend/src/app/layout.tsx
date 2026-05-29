import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Merited — GitHub → Hiring Decision",
  description: "Turn a GitHub profile into an instant recruiter-ready developer evaluation.",
  openGraph: {
    title: "Merited",
    description: "Turn a GitHub profile into a hiring decision.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="h-full bg-[#0a0a0a] text-white antialiased">{children}</body>
    </html>
  );
}
