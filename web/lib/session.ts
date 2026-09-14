import { cookies } from "next/headers";

const BASE = process.env.API_URL_INTERNAL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Me {
  id: string;
  email: string;
  plan: string;
  features: Record<string, boolean>;
}

/** Token da sessão (cookie httpOnly), disponível em server components. */
export function getToken(): string | undefined {
  return cookies().get("r3d_token")?.value;
}

/** Usuário logado, ou null. */
export async function getMe(): Promise<Me | null> {
  const token = getToken();
  if (!token) return null;
  const res = await fetch(`${BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}

export interface Usage {
  plan: string;
  used: number;
  limit: number | null;
  unlimited: boolean;
}

export async function getUsage(): Promise<Usage | null> {
  const token = getToken();
  if (!token) return null;
  const res = await fetch(`${BASE}/auth/me/usage`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!res.ok) return null;
  return res.json();
}
