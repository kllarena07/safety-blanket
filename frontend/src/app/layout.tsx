"use client";
import { Inter } from "next/font/google";
import { ClerkProvider, useUser } from "@clerk/nextjs";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>{children}
          <Navbar />
        </body>
      </html>
    </ClerkProvider>
  );
}
