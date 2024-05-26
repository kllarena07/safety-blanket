"use client";

import { useUser } from "@clerk/nextjs";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const [isToggled, setToggle] = useState(false);
  const { user } = useUser();
  const userPhone = user?.primaryPhoneNumber?.phoneNumber;

  console.log(pathname);

  const handleClick = () => {
    fetch(`http://localhost:8000/phone/${userPhone}`)
      .then((response) => response.json())
      .then((data) => console.log(data));
  }

  return (
    <>
      {isToggled ? (
        <section className="absolute translate-x-2/4 right-[50%] rounded-2xl w-[80vw] bottom-[108px] w-full bg-black flex flex-col items-center justify-center gap-5 h-[180px]">
          <a href='/'>Home</a>
          <a href='/chat'>Chat</a>
          <a href='/settings'>Settings</a>
        </section>
      ) : ''}
      <footer className="flex rounded-full justify-between bg-white p-3 mx-5">
        <button disabled={pathname === '/' ? true : false} className="disabled:opacity-50 disabled:cursor-not-allowed text-[#843232] bg-[#FFDBDB] rounded-full font-bold px-10 py-5 w-[80%]" onClick={() => handleClick()}>Call Companion</button>
        <button onClick={() => setToggle(!isToggled)} className="flex items-center justify-center bg-[#CC7178] w-[64px] h-[64px] rounded-full p-2.5">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="white" className="size-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
      </footer>
    </>
  )
}