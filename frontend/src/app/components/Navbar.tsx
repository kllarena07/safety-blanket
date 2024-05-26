"use client";

import { useState } from "react";

export default function Navbar() {
  const [isToggled, setToggle] = useState(false);

  return (
    <>
      {isToggled ? (
        <section className="absolute w-full top-[76px] bg-black flex flex-col h-[calc(100dvh-164px)] items-center justify-center gap-5">
        <a href='settings'>Home</a>
        <a href='settings'>Chat</a>
        <a href='settings'>Settings</a>
      </section>
      ) : ''}
      <section className="flex flex-col h-[calc(100dvh-164px)] items-center justify-center gap-5">
        <button onClick={() => setToggle(!isToggled)} className="bg-[#CC7178] text-black font-bold w-[200px] h-[200px] rounded-full">End Trip</button>
      </section>
      <footer className="flex rounded-full justify-between bg-white p-3 mx-5 mb-5">
        <button className="text-[#843232] bg-[#FFDBDB] rounded-full font-bold px-10 py-5 w-[80%]">Call Companion</button>
        <button onClick={() => setToggle(!isToggled)} className={`bg-[#CC7178] rounded-full p-2.5 transition-transform ${isToggled ? "rotate-90" : ''}`}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" className="h-full">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
      </footer>
    </>
  )
}
