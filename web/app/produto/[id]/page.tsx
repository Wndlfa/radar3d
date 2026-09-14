import { ProductDetail } from "@/components/ProductDetail";

// Página cheia — usada em acesso direto / recarregar. Quando a navegação vem
// de dentro do app, a intercepting route (app/@modal) abre o modal deslizante.
export default function ProductPage({ params }: { params: { id: string } }) {
  return <ProductDetail id={params.id} />;
}
