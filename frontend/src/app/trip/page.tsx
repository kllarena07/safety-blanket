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
    </main>
  )
}