import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "多市场投资分析工具",
  description: "A股、港股、美股、黄金与基金的 Streamlit 投资分析工具入口。",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
