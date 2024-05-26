"use client";

import Arrow from "./_arrow";
import { useEffect, useRef, useState } from "react";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputDisabled, setInputDisabled] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [socket, setSocket] = useState(null);
  const chatRef = useRef(null);
  
  useEffect(() => {
    // Create WebSocket connection.
    const ws = new WebSocket('ws://127.0.0.1:8000/ws?client_id=123');
    
    // Set up event handlers.
    ws.onopen = () => {
      console.log('WebSocket is open now.');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      console.log('WebSocket message received:', event);
      setInputDisabled(false);
      setMessages(prevMessages => [...prevMessages, JSON.parse(event.data)]);
      if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
    };

    ws.onclose = () => {
      console.log('WebSocket is closed now.');
    };

    // Clean up WebSocket connection when component unmounts.
    return () => {
      ws.close();
    };
  }, []);

  const appendNewMessage = (message: string) => {
    const data = {
      event: message.toLowerCase().includes("pineapple") ? "event" : "conversation-message",
      user_id: "12486353063",
      owner: "user",
      content: message
    };

    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;

    socket.send(JSON.stringify(data));
    setInputDisabled(true);
    setMessages(prevMessages => [ ...prevMessages, data ]);
    setInputValue("");
  }

  const handleKeyDown = (evt) => {
    if (evt.code === "Enter") appendNewMessage(inputValue);
  }

  return (
    <main className="flex flex-col white bg-[#E4EDEE] h-dvh w-full">
      <header className="py-5 bg-white text-center">
        <h1 className="text-3xl bg-white text-black font-bold">Check-in Chat</h1>
      </header>
      <section className="flex flex-col p-5 h-[calc(100dvh-76px)]">
        <section className="p-2 bg-[#232323] rounded-3xl h-[calc(100%-152px)]" ref={chatRef}>
            <ul className="overflow-y-scroll h-[calc(100%-44px)] flex flex-col">
              {messages.map(({ owner, content }, index) => (
                <li key={index} className={`${owner === "user" ? "self-end bg-[#FFDBDB]" : "self-start bg-[#CC7178]"} flex flex-col w-1/2 py-2 px-5 rounded-full text-black mb-5`}>
                  <p key={index}>{content}</p>
                </li>
              ))}
              {inputDisabled ? (
                <li className="self-start bg-[#CC7178] flex flex-col w-1/2 py-2 px-5 rounded-full text-black mb-5">
                  ...
                </li>
              ): ' '}
            </ul>
            <section className="flex w-full rounded-full bg-white overflow-hidden items-center">
              <input disabled={inputDisabled} onChange={(evt) => setInputValue(evt.target.value)} value={inputValue} placeholder="Send a message" type="text" className="w-full text-black p-2.5 disabled:cursor-not-allowed" onKeyDown={handleKeyDown} />
              <button className="mr-5" onClick={() => appendNewMessage(inputValue)}>
                <Arrow className="size-5" />
              </button>
            </section>
        </section>
        <section className="bg-[#CC7178] text-black font-bold p-5 rounded-full my-5">
          Next Check-in
        </section>

        <footer className="flex rounded-full justify-between bg-white p-3">
          <button className="text-[#843232] bg-[#FFDBDB] rounded-full font-bold px-10 py-5 w-[80%]">Call Companion</button>
          <a href='/profile' className="bg-[#CC7178] rounded-full p-2.5">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black" className="h-full">
              <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clipRule="evenodd" />
            </svg>
          </a>
        </footer>
      </section>
    </main>
  )
}