"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createProduct, type ProductInput } from "@/lib/api";

// Entrada curada de produtos da Shopee (MVP, ver docs/fontes.md §Mercado).
// O usuário cola os dados do anúncio; o backend já dispara a busca de modelos.
export default function AddProduct() {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const f = new FormData(e.currentTarget);
    const num = (k: string) => {
      const v = (f.get(k) as string)?.trim();
      return v ? Number(v) : null;
    };
    const payload: ProductInput = {
      title: (f.get("title") as string).trim(),
      image_url: (f.get("image_url") as string)?.trim() || null,
      price_brl: num("price_brl"),
      public_sales: num("public_sales"),
      trend: (f.get("trend") as string)?.trim() || null,
      shop_name: (f.get("shop_name") as string)?.trim() || null,
      competitors: num("competitors"),
      shopee_url: (f.get("shopee_url") as string)?.trim() || null,
    };
    try {
      const p = await createProduct(payload);
      router.push(`/produto/${p.id}`);
    } catch {
      setError("Não foi possível salvar. A API está rodando?");
      setSaving(false);
    }
  }

  const field =
    "w-full rounded-md border border-border bg-bg px-3 py-2 text-sm text-text placeholder:text-faint focus:border-accent focus:outline-none";
  const label = "mb-1 block text-xs font-medium text-muted";

  return (
    <div className="mx-auto max-w-xl">
      <Link href="/" className="text-sm text-accent hover:underline">
        ← Voltar
      </Link>
      <h1 className="mt-3 text-xl font-semibold">Adicionar produto da Shopee</h1>
      <p className="mt-1 text-sm text-muted">
        Cole os dados de um anúncio real. Ao salvar, o Radar3D busca modelos
        semelhantes nas bibliotecas e classifica a licença automaticamente.
      </p>

      <form onSubmit={onSubmit} className="mt-5 space-y-4">
        <div>
          <label className={label} htmlFor="title">
            Título do anúncio *
          </label>
          <input
            id="title"
            name="title"
            required
            placeholder="Ex.: Suporte de controle cabeça de dragão para videogame"
            className={field}
          />
          <p className="mt-1 text-xs text-faint">
            Use o título completo e descritivo do anúncio — ele guia a busca.
          </p>
        </div>

        <div>
          <label className={label} htmlFor="image_url">
            URL da foto do produto
          </label>
          <input id="image_url" name="image_url" type="url" placeholder="https://..." className={field} />
          <p className="mt-1 text-xs text-faint">
            Link direto da imagem principal do anúncio (usada no match visual).
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={label} htmlFor="price_brl">Preço (R$)</label>
            <input id="price_brl" name="price_brl" type="number" step="0.01" className={field} />
          </div>
          <div>
            <label className={label} htmlFor="public_sales">Vendas públicas</label>
            <input id="public_sales" name="public_sales" type="number" className={field} />
          </div>
          <div>
            <label className={label} htmlFor="trend">Tendência</label>
            <input id="trend" name="trend" placeholder="crescendo" className={field} />
          </div>
          <div>
            <label className={label} htmlFor="competitors">Concorrentes</label>
            <input id="competitors" name="competitors" type="number" className={field} />
          </div>
          <div>
            <label className={label} htmlFor="shop_name">Loja</label>
            <input id="shop_name" name="shop_name" className={field} />
          </div>
          <div>
            <label className={label} htmlFor="shopee_url">Link da Shopee</label>
            <input id="shopee_url" name="shopee_url" type="url" placeholder="https://shopee.com.br/..." className={field} />
          </div>
        </div>

        {error && <p className="text-sm text-lic-red">{error}</p>}

        <button
          type="submit"
          disabled={saving}
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60"
        >
          {saving ? "Salvando e buscando modelos…" : "Salvar e buscar modelos"}
        </button>
      </form>
    </div>
  );
}
