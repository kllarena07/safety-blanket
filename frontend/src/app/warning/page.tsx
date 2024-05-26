import WarningImage from './warning.png'
import Image from 'next/image'

export default function Warning() {
  return (
    <main>
      <header className="py-5 bg-white text-center">
        <h1 className="text-3xl bg-white text-black font-bold text-black">Unsafe Conditions Detected</h1>
      </header>
      <section className='flex flex-col justify-center items-center gap-5 font-bold bg-[#E4EDEE] h-[calc(100dvh-76px)]'>
        <Image src={WarningImage} alt="Warning" width="300" />
        <h2 className='text-2xl text-red-500'>Unsafe Conditions Detected</h2>
        <p className='text-black'>Calling trusted personnel...</p>
      </section>
    </main>
  )
}