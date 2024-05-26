"use client";
import { SignUpButton, SignInButton, SignedIn, SignedOut, SignOutButton } from "@clerk/nextjs";
import Head from "next/head";
import Image from "next/image";
import BlanketGirl from "/public/blanket-girl.png"

export default function Home() {
  return (
    <main className="flex flex-col bg-[#E4EDEE] h-screen w-full">
      <SignedOut>
        <Head>
          <title>Safety Blanket</title>
        </Head>
        <div className="flex justify-center items-center h-screen bg-[#EF9F96]">
          <div className="text-center p-5 rounded-lg">
            <h1 className="text-5xl text-black font-bold mb-4">Safety Blanket</h1>
            <div className="flex justify-center w-[100%]">
              <Image src={BlanketGirl} alt="Safety Blanket" className="w-70 mb-5" />
            </div>
            <div className="flex flex-col justify-center items-center space-y-4">
              <div className="flex justify-center text-lg text-black font-semibold bg-[#FFDBDB] rounded-full shadow-md hover:bg-[#FFFFFF] focus:outline-none focus:ring-2 focus:ring-opacity-75 px-10 py-5 w-[50%]">
                <SignInButton />
              </div>
              <div className="flex justify-center text-lg text-black font-semibold bg-[#FFDBDB] rounded-full shadow-md hover:bg-[#FFFFFF] focus:outline-none focus:ring-2 focus:ring-opacity-75 px-10 py-5 w-[50%]">
                <SignUpButton />
              </div>
            </div>
          </div>
        </div>
      </SignedOut>

      <SignedIn>
        <div className="flex flex-col bg-[#E4EDEE] h-screen w-full">
          <header className="py-5 bg-white text-center">
            <h1 className="text-3xl bg-white text-black font-bold">Safety Blanket</h1>
          </header>
          <div className="flex h-[calc(100dvh-164px)] flex-col justify-center items-center space-y-4">
            <section className="flex items-center justify-center gap-5 w-[90%]">
              <a href='/timer' className="flex items-center justify-center bg-[#CC7178] text-black font-bold w-[200px] h-[200px] rounded-full">Start Safety Timer</a>
              <a href='/trip' className="flex items-center justify-center bg-[#CC7178] text-black font-bold w-[200px] h-[200px] rounded-full">Start Trip</a>
            </section>
            <div className="flex justify-center text-lg text-black font-semibold bg-[#FFDBDB] rounded-full shadow-md hover:bg-[#FFFFFF] focus:outline-none focus:ring-2 focus:ring-opacity-75 px-10 py-5 w-[50%]">
              <SignOutButton />
            </div>
          </div>
        </div>
      </SignedIn>
    </main>
  );
}
