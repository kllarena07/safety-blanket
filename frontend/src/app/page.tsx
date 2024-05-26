"use client";
import { SignUpButton, SignInButton, SignedIn, SignedOut, useUser, SignOutButton } from "@clerk/nextjs";
import { useRouter } from "next/router";
import { useEffect } from "react";
import Head from "next/head";
import Image from "next/image";

export default function Home() {
  const handleTimer = async () => {

  }
  const handleTrip = async () => {

  }

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
            <img src="blanket-girl.png" alt="Safety Blanket" className="w-70 mb-5" />
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
            <button onClick={handleTimer} className="bg-[#CC7178] text-black font-bold w-[200px] h-[200px] rounded-full">Start Safety Timer</button>
            <button onClick={handleTrip} className="bg-[#CC7178] text-black font-bold w-[200px] h-[200px] rounded-full">Start Trip</button>
          </section>
          <div className="flex justify-center text-lg text-black font-semibold bg-[#FFDBDB] rounded-full shadow-md hover:bg-[#FFFFFF] focus:outline-none focus:ring-2 focus:ring-opacity-75 px-10 py-5 w-[50%]">
            <SignOutButton />
          </div>
        </div>
        <footer className="flex rounded-full justify-between bg-white p-3 mx-5 mb-5">
          <button className="text-[#843232] bg-[#FFDBDB] rounded-full font-bold px-10 py-5 w-[80%]">Call Companion</button>
          <a href='/settings' className="bg-[#CC7178] rounded-full p-2.5">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black" className="h-full">
              <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clipRule="evenodd" />
            </svg>
          </a>
        </footer>
      </div>
      </SignedIn>
    </main>
  );
}
