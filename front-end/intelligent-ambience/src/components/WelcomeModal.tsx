"use client"
import { useState } from "react";
import Link from "next/link"

export default function WelcomeModal(props: {isOpen: boolean}) {

    const [isOpen, setIsOpen] = useState(props.isOpen);
    const handleClose = () => {
        setIsOpen(false);

    }
    return (
        <>
        {isOpen && (
        <div className="h-screen w-screen flex flex-col items-center justify-center">
        <div className="lg:w-[25%] w-[90%] bg-white rounded-lg p-6 shadow-md">
            <h1 className="text-4xl font-bold mb-4">Agentic Ambience</h1>
            <p className="mb-4">A transparent experiment in collective sound generation and sharing.</p>
            <div className="flex justify-end">
                <Link href="/generate">
                    <button onClick={handleClose} className="bg-blue-500 text-white px-4 py-2 rounded cursor-pointer">Start</button>
                </Link>
            </div>
        </div>
        </div>
        )}
        </>
    );
}
