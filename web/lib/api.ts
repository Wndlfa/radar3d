import type { KpiPoint, Product, ProductDetail, Trending } from "./types";

// Estas chamadas rodam em server components (dentro do container web), onde
// "localhost" é o próprio web — não a API. Server-side usa o host interno do
// Docker (api:8000); no browser, usaríamos NEXT_PUBLIC_API_URL.
const BASE =
  process.env.API_URL_INTERNAL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

function authHeaders(token?: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export interface ListParams {
  commercialOnly?: boolean;
  q?: string;
  sort?: "sales" | "price_asc" | "price_desc";
}

export async function listProducts(
  params: ListParams = {},
  token?: string,
): Promise<Product[]> {
  const url = new URL(`${BASE}/products`);
  if (params.commercialOnly) url.searchParams.set("commercial_only", "true");
  if (params.q) url.searchParams.set("q", params.q);
  if (params.sort) url.searchParams.set("sort", params.sort);
  const res = await fetch(url, { cache: "no-store", headers: authHeaders(token) });
  if (!res.ok) {
    // Surfaça a mensagem da API (ex.: 402 do filtro comercial = recurso Pro).
    const detail = await res
      .json()
      .then((d) => d?.detail)
      .catch(() => null);
    throw new Error(detail || "Falha ao carregar produtos");
  }
  return res.json();
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function getProduct(id: string, token?: string): Promise<ProductDetail> {
  const res = await fetch(`${BASE}/products/${id}`, {
    cache: "no-store",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const detail = await res
      .json()
      .then((d) => d?.detail)
      .catch(() => null);
    throw new ApiError(res.status, detail || "Falha ao carregar produto");
  }
  return res.json();
}

export async function listTrending(
  period: "day" | "week" | "month" = "week",
  token?: string,
): Promise<Trending[]> {
  const res = await fetch(`${BASE}/products/trending?period=${period}`, {
    cache: "no-store",
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error("Falha ao carregar tendências");
  return res.json();
}

export async function listKpis(days = 30, token?: string): Promise<KpiPoint[]> {
  try {
    const res = await fetch(`${BASE}/products/kpis?days=${days}`, {
      cache: "no-store",
      headers: authHeaders(token),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data?.points) ? data.points : [];
  } catch {
    return []; // sparkline é enfeite — nunca derruba a home
  }
}

export interface ProductInput {
  title: string;
  image_url?: string | null;
  price_brl?: number | null;
  public_sales?: number | null;
  trend?: string | null;
  shop_name?: string | null;
  competitors?: number | null;
  shopee_url?: string | null;
}

export async function createProduct(payload: ProductInput): Promise<Product> {
  const res = await fetch(`${BASE}/products`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Falha ao criar produto");
  return res.json();
}
