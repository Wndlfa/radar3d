import { Modal } from "@/components/Modal";
import { ProductDetail } from "@/components/ProductDetail";

// Intercepta a navegação para /produto/[id] vinda de dentro do app e a
// renderiza no slot @modal (painel deslizante). Acesso direto/refresh cai na
// página cheia em app/produto/[id]/page.tsx.
export default function ProductModal({ params }: { params: { id: string } }) {
  return (
    <Modal>
      <ProductDetail id={params.id} modal />
    </Modal>
  );
}
