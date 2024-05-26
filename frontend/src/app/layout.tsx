import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Safety Blanket",
  description: "A safety app for females",
  category: "website",
  generator: "Next.js",
  manifest: "/manifest.json",
  icons: [
    {
      rel: 'apple-touch-icon',
      url: '/icons/apple-touch-icon.png',
    },
    {
      rel: 'icon',
      url: '/icons/favicon-32x32.png',
    },
    {
      rel: 'icon',
      url: '/icons/favicon-16x16.png',
    },
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {

  return (
    <ClerkProvider>
      <html lang="en">
        <body className={`${inter.className} h-dvh`}>
          <main className="h-[calc(100%-108px)]">
            {children}
          </main>
          <Navbar />
        </body>
      </html>
    </ClerkProvider>
  );
}
