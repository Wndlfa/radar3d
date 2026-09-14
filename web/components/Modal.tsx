"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

// Painel deslizante (slide-over) para a intercepting route do detalhe.
// Fechar volta na história (router.back), desmontando o slot @modal e
// revelando a lista por baixo — sem recarregar.
export function Modal({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  function close() {
    router.back();
  }

  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") close();
    }
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex justify-end" role="dialog" aria-modal="true">
      <button
        aria-label="Fechar"
        onClick={close}
        className="absolute inset-0 h-full w-full cursor-default bg-black/50 backdrop-blur-sm"
      />
      <div className="modal-panel relative z-10 flex h-full w-full max-w-xl flex-col overflow-y-auto border-l border-border bg-bg shadow-pop">
        <button
          onClick={close}
          aria-label="Fechar"
          className="absolute right-4 top-4 z-20 grid h-9 w-9 place-items-center rounded-full border border-border bg-surface/80 text-muted backdrop-blur transition-colors hover:text-text"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden>
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
        <div className="p-5 md:p-6">{children}</div>
      </div>
    </div>
  );
}
