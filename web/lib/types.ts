// Espelha os schemas do backend (radar3d/schemas.py).
// Na Fase 1 gerar estes tipos a partir do OpenAPI da API.

export type LicenseTier =
  | "VENDA_PERMITIDA"
  | "EXIGE_LICENCA"
  | "SOMENTE_PESSOAL"
  | "NAO_IDENTIFICADA";

export interface Model3D {
  id: string;
  platform: string;
  title: string;
  creator: string | null;
  thumbnail_url: string | null;
  source_url: string;
  is_paid: boolean;
  price_brl: number | null;
  downloads: number | null;
  rating: number | null;
  license_tier: LicenseTier;
  license_raw: string | null;
  possible_protected_ip: boolean;
  license_checked_at: string | null;
}

export interface Match {
  final_score: number;
  match_level: number;
  model: Model3D;
}

export interface Product {
  id: string;
  title: string;
  image_url: string | null;
  price_brl: number | null;
  public_sales: number | null;
  trend: string | null;
  rating: number | null;
  shop_name: string | null;
  competitors: number | null;
  shopee_url: string | null;
  collected_at: string;
  models_count?: number;
  commercial_available?: boolean;
  best_license_tier?: LicenseTier | null;
  protected_ip?: boolean;
}

export interface ProductDetail extends Product {
  matches: Match[];
}

export interface Trending extends Product {
  period: string;
  growth_abs: number | null;
  growth_pct: number | null;
  first_sales: number | null;
  last_sales: number | null;
}
