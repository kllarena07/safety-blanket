"use client";

export default function Timer() {
  const handleEndTrip = async () => {

  }

  return (
    <main className="flex flex-col white bg-[#E4EDEE] h-dvh w-full">
      <header className="py-5 bg-white text-center">
        <h1 className="text-3xl bg-white text-black font-bold">Trip</h1>
      </header>
      <section className="flex flex-col h-[calc(100dvh-164px)] items-center justify-center gap-5">
        <button onClick={handleEndTrip} className="bg-[#CC7178] text-black font-bold w-[200px] h-[200px] rounded-full">End Trip</button>
      </section>
      <footer className="flex rounded-full justify-between bg-white p-3 mx-5 mb-5">
        <button className="text-[#843232] bg-[#FFDBDB] rounded-full font-bold px-10 py-5 w-[80%]">Call Companion</button>
        <a href='/settings' className="bg-[#CC7178] rounded-full p-2.5">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black" className="h-full">
            <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clipRule="evenodd" />
          </svg>
        </a>
      </footer>
    </main>
  )
}