'use client'
import { useState, useEffect } from 'react';
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


export default function Timer() {
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

    const [selectedTime, setSelectedTime] = useState(1);
    const [timeLeft, setTimeLeft] = useState(null);
    const [isRunning, setIsRunning] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [password, setPassword] = useState('');
    const [alertMe, setAlert] = useState(false);

    useEffect(() => {
        if (!userPhone) return;
        fetch(`https://0072-128-195-97-152.ngrok-free.app/user/${userPhone}`)
            .then((res) => res.json())
            .then((data) => {
                // Data might be empty
                if (data) {
                    setUserData(data);
                }
            })
            .catch((err) => {
                console.error(err);
            });
    }, [userPhone]);

    const handleStart = () => {
        setTimeLeft(selectedTime * 60);
        setIsRunning(true);
    };

    const handleCancel = () => {
        setShowModal(true);
    };

    const handlePasswordSubmit = () => {
        if (password === userData.timer_passcode) {
            setShowModal(false);
            setIsRunning(false);
            setTimeLeft(null);
        } else {
            setShowModal(false);
        }
    };

    useEffect(() => {
        let timer;
        if (isRunning && timeLeft > 0) {
            timer = setInterval(() => {
                setTimeLeft(timeLeft - 1);
            }, 1000);
        } else if (isRunning && timeLeft === 0) {
            clearInterval(timer);
            setIsRunning(false);
            fetch(`https://0072-128-195-97-152.ngrok-free.app/emergency/${userPhone}`)
                .then((response) => response.json())
                .then((data) => console.log(data));
            alert('Alerting emergency contact');
            setAlert(true);

        }
        return () => clearInterval(timer);
    }, [isRunning, timeLeft]);

    useEffect(() => {
        if (timeLeft <= 10 && timeLeft > 0) {
            setAlert(true);
        } else {
            setAlert(false);
        }
    }, [timeLeft]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen py-2 bg-gray-900 text-white">
            <Head>
                <title>Timer</title>
            </Head>

            <div className="flex flex-col items-center">
                <div className="text-2xl font-bold mb-4 text-white">Timer</div>
                {!isRunning ? (
                    <div>
                        <select
                            className="mb-4 p-2 border border-gray-600 bg-gray-800 text-white rounded"
                            value={selectedTime}
                            onChange={(e) => setSelectedTime(e.target.value)}
                        >
                            <option value={1}>1 Minute</option>
                            <option value={5}>5 Minutes</option>
                            <option value={10}>10 Minutes</option>
                            <option value={15}>15 Minutes</option>
                            <option value={20}>20 Minutes</option>
                        </select>
                        <button
                            className="px-4 py-2 bg-blue-500 text-white rounded"
                            onClick={handleStart}
                        >
                            Start
                        </button>
                    </div>
                ) : (
                    <div className="flex flex-col items-center">
                        <div className={`text-4xl ${alertMe ? 'animate-ping' : ''}`}>
                            {Math.floor(timeLeft / 60)}:{('0' + (timeLeft % 60)).slice(-2)}
                        </div>
                        <button
                            className="mt-4 px-4 py-2 bg-red-500 text-white rounded"
                            onClick={handleCancel}
                        >
                            Cancel
                        </button>
                    </div>
                )}
            </div>

            {showModal && (
                <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-75">
                    <div className="bg-gray-900 p-4 rounded">
                        <input
                            type="password"
                            className="mb-4 p-2 border border-gray-600 bg-gray-800 text-white rounded w-full"
                            placeholder="Enter Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <button
                            className="px-4 py-2 bg-green-500 text-white rounded"
                            onClick={handlePasswordSubmit}
                        >
                            Submit
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
