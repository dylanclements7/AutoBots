"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Run only on client side
    const user = localStorage.getItem("user");

    if (!user) {
      router.replace("/login");
    } else {
      router.replace("/game");
    }
  }, [router]);

  return (
    <div className="flex h-screen items-center justify-center">
      <p>Checking user session...</p>
    </div>
  );
}
