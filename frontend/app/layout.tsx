import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import Sidebar from "../components/Sidebar";
import "./globals.css";

export const metadata: Metadata = { title: "ShadowAI Guardian", description: "Agentic Privacy Firewall for GenAI Tool Usage" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Sidebar />
        <main className="ml-64 min-h-screen p-6">{children}</main>
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
