import { Metadata } from "next";
import { ProfileData } from "@/types";
import SharedProfileClient from "./SharedProfileClient";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getProfile(username: string): Promise<ProfileData | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/profile/${username}`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: { username: string };
}): Promise<Metadata> {
  const profile = await getProfile(params.username);
  if (!profile) {
    return { title: "Profile not found — Merited" };
  }
  return {
    title: `${profile.name || profile.username} — Merited Developer Profile`,
    description: profile.recommendation.summary,
  };
}

export default async function SharedProfilePage({
  params,
}: {
  params: { username: string };
}) {
  const profile = await getProfile(params.username);
  return <SharedProfileClient profile={profile} username={params.username} />;
}
