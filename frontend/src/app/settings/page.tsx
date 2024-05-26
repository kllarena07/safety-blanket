"use client"
import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import Head from 'next/head';

interface Contact {
  name: string;
  phoneNumber: string;
}

const SettingsPage: React.FC = () => {
  const [preferredNumber, setPreferredNumber] = useState('+1 (626) 000-0000');
  const [timerPasscode, setTimerPasscode] = useState('1234');
  const [emergencyCodeWords, setEmergencyCodeWords] = useState('');
  const [emergencyContacts, setEmergencyContacts] = useState<Contact[]>([
    { name: 'Alice', phoneNumber: '+1 (555) 123-4567' },
    { name: 'Bob', phoneNumber: '+1 (555) 234-5678' },
  ]);

  const [editingField, setEditingField] = useState<string | null>(null);
  const [currentContactIndex, setCurrentContactIndex] = useState<number | null>(null);

  const handleSave = () => {
    setEditingField(null);
    setCurrentContactIndex(null);
    // api
  };

  const handleCancel = () => {
    setEditingField(null);
    setCurrentContactIndex(null);
    // api
    setPreferredNumber('+1 (626) 000-0000');
    setTimerPasscode('1234');
    setEmergencyCodeWords('');
    setEmergencyContacts([
      { name: 'John Smith', phoneNumber: '+1 (123) 456-7890' },
      { name: 'Jane Doe', phoneNumber: '+1 (123) 456-7890' },
    ]);
  };

  return (
    <>
      <Head>
        <title>User Settings</title>
      </Head>
      <div className="min-h-screen bg-gray-100 flex flex-col items-center py-10">
        <div className="bg-white shadow-md rounded-lg p-8 w-11/12 md:w-2/3 lg:w-1/2">
          <div className="flex items-center mb-6">
            <div className="w-20 h-20 rounded-full overflow-hidden border-2 border-gray-300 mr-4">
              <Image
                src="/path-to-image.jpg" // api
                alt="Jane Smith"
                width={80}
                height={80}
                className="object-cover"
              />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Jane Smith</h1>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Preferred Number:</label>
            {editingField === 'preferredNumber' ? (
              <div>
                <input
                  type="text"
                  value={preferredNumber}
                  onChange={(e) => setPreferredNumber(e.target.value)}
                  className="w-full p-2 border rounded bg-gray-50 text-gray-800"
                />
                <div className="flex justify-between mt-2">
                  <button
                    onClick={handleSave}
                    className="py-2 px-4 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleCancel}
                    className="py-2 px-4 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-2 border rounded bg-gray-50 text-gray-800 flex justify-between items-center">
                <span>{preferredNumber}</span>
                <button
                  className="ml-4 px-2 py-1 bg-blue-500 text-white text-sm font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
                  onClick={() => setEditingField('preferredNumber')}
                >
                  Edit
                </button>
              </div>
            )}
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Timer Passcode:</label>
            {editingField === 'timerPasscode' ? (
              <div>
                <input
                  type="text"
                  value={timerPasscode}
                  onChange={(e) => setTimerPasscode(e.target.value)}
                  className="w-full p-2 border rounded bg-gray-50 text-gray-800"
                />
                <div className="flex justify-between mt-2">
                  <button
                    onClick={handleSave}
                    className="py-2 px-4 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleCancel}
                    className="py-2 px-4 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-2 border rounded bg-gray-50 text-gray-800 flex justify-between items-center">
                <span>{timerPasscode}</span>
                <button
                  className="ml-4 px-2 py-1 bg-blue-500 text-white text-sm font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
                  onClick={() => setEditingField('timerPasscode')}
                >
                  Edit
                </button>
              </div>
            )}
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">Emergency Code Words:</label>
            {editingField === 'emergencyCodeWords' ? (
              <div>
                <input
                  type="text"
                  value={emergencyCodeWords}
                  onChange={(e) => setEmergencyCodeWords(e.target.value)}
                  className="w-full p-2 border rounded bg-gray-50 text-gray-800"
                />
                <div className="flex justify-between mt-2">
                  <button
                    onClick={handleSave}
                    className="py-2 px-4 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleCancel}
                    className="py-2 px-4 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="p-2 border rounded bg-gray-50 text-gray-800 flex justify-between items-center">
                <span>{emergencyCodeWords || 'None'}</span>
                <button
                  className="ml-4 px-2 py-1 bg-blue-500 text-white text-sm font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
                  onClick={() => setEditingField('emergencyCodeWords')}
                >
                  Edit
                </button>
              </div>
            )}
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">Emergency Contacts:</label>
            {emergencyContacts.map((contact, index) => (
              <div key={index} className="mb-4">
                {editingField === 'emergencyContacts' && currentContactIndex === index ? (
                  <div>
                    <input
                      type="text"
                      value={contact.name}
                      onChange={(e) => {
                        const newContacts = [...emergencyContacts];
                        newContacts[index].name = e.target.value;
                        setEmergencyContacts(newContacts);
                      }}
                      placeholder="Name"
                      className="w-full p-2 border rounded bg-gray-50 text-gray-800 mb-2"
                    />
                    <input
                      type="text"
                      value={contact.phoneNumber}
                      onChange={(e) => {
                        const newContacts = [...emergencyContacts];
                        newContacts[index].phoneNumber = e.target.value;
                        setEmergencyContacts(newContacts);
                      }}
                      placeholder="Phone Number"
                      className="w-full p-2 border rounded bg-gray-50 text-gray-800"
                    />
                    <div className="flex justify-between mt-2">
                      <button
                        onClick={handleSave}
                        className="py-2 px-4 bg-green-500 text-white font-semibold rounded-lg shadow-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75"
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancel}
                        className="py-2 px-4 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-75"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="p-2 border rounded bg-gray-50 text-gray-800 flex justify-between items-center">
                    <div>
                      <p>{contact.name}</p>
                      <p>{contact.phoneNumber}</p>
                    </div>
                    <button
                      className="ml-4 px-2 py-1 bg-blue-500 text-white text-sm font-semibold rounded-lg shadow-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
                      onClick={() => {
                        setEditingField('emergencyContacts');
                        setCurrentContactIndex(index);
                      }}
                    >
                      Edit
                    </button>
                  </div>
                )}
              </div>
            ))}
            <Link href="/settings/contacts" legacyBehavior>
              <a className="mt-4 block text-center py-2 px-4 bg-gray-800 text-white font-semibold rounded-lg shadow-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-600 focus:ring-opacity-75">
                Update
              </a>
            </Link>
          </div>
        </div>


      </div>
    </>
  );
};

export default SettingsPage;
