"use client";
import { SignUpButton, SignInButton, UserButton, useUser } from "@clerk/nextjs";
import Head from "next/head"
import Image from "next/image";

export default function Home() {
  const { isSignedIn } = useUser();

  return (
    <main className="flex flex-col bg-[#E4EDEE] h-screen w-full">
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
    </main>
  );
}
