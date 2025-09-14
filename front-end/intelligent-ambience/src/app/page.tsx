"use client"

import WelcomeModal from "@/components/WelcomeModal"
import Generate from "@/app/generate/page"
import { useState } from "react";

export default function Home() {
  const [isOpen, setIsOpen] = useState(true);
  return (
    <>
      <WelcomeModal isOpen={isOpen} />
      <Generate />
    </>
  );
}
