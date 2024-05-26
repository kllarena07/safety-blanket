"use client"
import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Head from 'next/head';
import { useUser } from '@clerk/nextjs';

interface UserData {
  name: string;
  emergency_number: string;
  timer_passcode: string;
  keyword: string;
  last_location: string;
  last_updated: string;
}

const SettingsPage: React.FC = () => {
  const { user } = useUser();
  const userPhone = user?.primaryPhoneNumber?.phoneNumber
  const [userData, setUserData] = useState<UserData>({
    name: '',
    emergency_number: '',
    timer_passcode: '',
    keyword: '',
    last_location: '',
    last_updated: '',
  });

  useEffect(() => {
    if (!userPhone) return;
    fetch(`http://localhost:8000/user/${userPhone}`)
      .then((res) => res.json())
      .then((data) => {
        setUserData(data);
      })
      .catch((err) => {
        console.error(err);
      });
  }, [userPhone]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSave = () => {
    // Make a post request to same url
    fetch(`http://localhost:8000/user/${userPhone}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
      })
      .catch((err) => {
        console.error(err);
      });
  };

  return (
    <>
      <Head>
        <title>User Settings</title>
      </Head>
      <div className="min-h-screen bg-gray-100 flex flex-col items-center py-10">
        <div className="bg-white shadow-md rounded-lg p-8 w-11/12 md:w-2/3 lg:w-1/2">
          <div className="flex items-center mb-6">

            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                User Settings for {userPhone}
              </h1>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Name:</label>
            <input
              type="text"
              name="name"
              value={userData.name}
              onChange={handleInputChange}
              className="w-full p-2 border rounded bg-gray-50 text-gray-800"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Preferred Number:</label>
            <input
              type="text"
              name="emergency_number"
              value={userData.emergency_number}
              onChange={handleInputChange}
              className="w-full p-2 border rounded bg-gray-50 text-gray-800"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Timer Passcode:</label>
            <input
              type="text"
              name="timer_passcode"
              value={userData.timer_passcode}
              onChange={handleInputChange}
              className="w-full p-2 border rounded bg-gray-50 text-gray-800"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Emergency Code Words:</label>
            <input
              type="text"
              name="keyword"
              value={userData.keyword}
              onChange={handleInputChange}
              className="w-full p-2 border rounded bg-gray-50 text-gray-800"
            />
          </div>

          <div className="flex justify-center mt-4">
            <button
              onClick={handleSave}
              className="py-2 px-4 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default SettingsPage;
