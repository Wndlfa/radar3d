import Link from "next/link";
import { getProduct, ApiError } from "@/lib/api";
import { getToken } from "@/lib/session";
import { ModelRow } from "@/components/ModelRow";
import { AutoRefresh } from "@/components/AutoRefresh";

export default async function ProductPage({ params }: { params: { id: string } }) {
  let product;
  try {
    product = await getProduct(params.id, getToken());
  } catch (e) {
    const status = e instanceof ApiError ? e.status : 0;
    const message = e instanceof Error ? e.message : "Erro ao carregar.";
    return (
      <div className="mx-auto max-w-md text-center">
        <Link href="/" className="text-sm text-accent hover:underline">
          ← Voltar
        </Link>
        <div className="mt-6 rounded-lg border border-border bg-surface p-6">
          {status === 401 ? (
            <>
              <p className="font-medium">Entre para ver os modelos encontrados</p>
              <p className="mt-1 text-sm text-muted">
                A lista de modelos e as licenças ficam disponíveis para usuários logados.
              </p>
              <Link
                href="/login"
                className="mt-4 inline-block rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover"
              >
                Entrar / criar conta
              </Link>
            </>
          ) : (
            <>
              <p className="font-medium text-lic-yellow">{message}</p>
              {status === 402 && (
                <p className="mt-1 text-sm text-muted">
                  Assine o Pro para consultas ilimitadas.
                </p>
              )}
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <Link href="/" className="text-sm text-accent hover:underline">
        ← Voltar
      </Link>

      {/* Área comercial */}
      <section className="mt-3 rounded-lg border border-border bg-surface p-4">
        <div className="flex gap-4">
          <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded bg-surface-2">
            {product.image_url && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={product.image_url} alt="" className="h-full w-full object-cover" />
            )}
          </div>
          <div>
            <h1 className="text-lg font-semibold">{product.title}</h1>
            <p className="mt-1 font-mono">
              {product.price_brl != null && (
                <span className="font-semibold">R$ {product.price_brl.toFixed(2)}</span>
              )}
              {product.public_sales != null && (
                <span className="text-muted"> · {product.public_sales} vendas</span>
              )}
              {product.trend && <span className="text-lic-green"> · ↑ {product.trend}</span>}
            </p>
            <p className="mt-0.5 text-xs text-muted">
              {product.rating != null && `★ ${product.rating} · `}
              {product.shop_name}
              {product.competitors != null && ` · ${product.competitors} concorrentes`}
            </p>
            {product.shopee_url && (
              // shopee_url carrega o offerLink (link de afiliado) quando a fonte
              // é a API oficial/apify. rel="sponsored" é a marcação correta.
              <a
                href={product.shopee_url}
                target="_blank"
                rel="sponsored noopener noreferrer"
                className="mt-2 inline-block rounded-md bg-[#ee4d2d] px-3 py-1.5 text-sm font-medium text-white hover:opacity-90"
              >
                Comprar na Shopee ↗
              </a>
            )}
          </div>
        </div>
      </section>

      {/* Arquivos encontrados */}
      <section className="mt-6">
        <h2 className="mb-3 font-semibold">
          Modelos encontrados ({product.matches.length})
        </h2>
        {product.matches.length === 0 ? (
          <AutoRefresh active={true} />
        ) : (
          <div className="space-y-2">
            {product.matches.map((m) => (
              <ModelRow key={m.model.id} match={m} />
            ))}
          </div>
        )}
        <p className="mt-3 text-xs text-faint">
          A semelhança indica quão parecidos os itens são — não prova que o modelo
          originou o anúncio. Confira sempre a licença na página do criador.
        </p>
      </section>
    </div>
  );
}
