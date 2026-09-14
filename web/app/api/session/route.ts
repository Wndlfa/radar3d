// Sessão via cookie httpOnly: o browser fala com este route handler (server),
// que chama a API FastAPI e guarda o token num cookie que os server components
// conseguem ler. O token nunca fica exposto ao JS do browser.
const API = process.env.API_URL_INTERNAL ?? "http://api:8000";
const COOKIE = "r3d_token";

export async function POST(req: Request) {
  const { mode, email, password } = await req.json();
  const path = mode === "register" ? "/auth/register" : "/auth/login";

  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    return Response.json(
      { error: data?.detail || "Falha na autenticação" },
      { status: res.status },
    );
  }

  const out = Response.json({ plan: data.plan });
  out.headers.append(
    "Set-Cookie",
    `${COOKIE}=${data.token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${7 * 24 * 3600}`,
  );
  return out;
}

export async function DELETE() {
  const out = Response.json({ ok: true });
  out.headers.append("Set-Cookie", `${COOKIE}=; Path=/; HttpOnly; Max-Age=0`);
  return out;
}
