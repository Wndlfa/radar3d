"""Tarefas de coleta + matching + classificação de licença.

Fluxo (ver docs/regras-de-negocio.md §4):
  produto -> busca nas fontes -> classifica licença -> calcula match -> persiste.

O matching usa embeddings (CLIP self-hosted por padrão no worker): compara a
foto do anúncio com o render do modelo (visual) e o título com o nome (texto).
Ver docs/plano §Fase 3. O provider é trocável (stub/local_clip/api).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from radar3d.db import SessionLocal
from radar3d.domain.licenses import classify_license
from radar3d.domain.matching import combine
from radar3d.embeddings import cosine
from radar3d.embeddings.factory import get_provider
from radar3d.models import Embedding, Model3D, Product, ProductModelMatch
from radar3d.sources.registry import enabled_adapters
from radar3d.translate.factory import get_translator


def _store_embedding(
    session: Session, owner_type: str, owner_id: str, kind: str, vec: list[float] | None
) -> None:
    """Guarda (upsert) o vetor para reuso/ANN futuro. None => não guarda."""
    if vec is None:
        return
    row = session.scalars(
        select(Embedding).where(
            Embedding.owner_type == owner_type,
            Embedding.owner_id == owner_id,
            Embedding.kind == kind,
        )
    ).first()
    if row is None:
        session.add(
            Embedding(owner_type=owner_type, owner_id=owner_id, kind=kind, vector=vec)
        )
    else:
        row.vector = vec


def enrich_product(product_id: str) -> int:
    """Busca modelos semelhantes para um produto e persiste os matches.

    Retorna a quantidade de matches criados/atualizados.
    """
    session = SessionLocal()
    try:
        product = session.get(Product, product_id)
        if product is None:
            return 0

        provider = get_provider()

        # Título da Shopee (PT) -> EN: usado tanto na busca quanto no match
        # textual (as bibliotecas são em inglês). Ver docs/plano §Fase 3.
        query = get_translator().to_english(product.title)

        # Embeddings do produto (texto + imagem), calculados uma vez.
        prod_text_vec = provider.embed_texts([query])[0]
        prod_img_vec = provider.embed_image_urls([product.image_url])[0]
        _store_embedding(session, "product", product.id, "text", prod_text_vec)
        _store_embedding(session, "product", product.id, "image", prod_img_vec)

        count = 0
        for adapter in enabled_adapters():
            raws = [
                r
                for r in adapter.search(query, limit=20)
                if r.external_id and r.source_url
            ]
            if not raws:
                continue

            # Embeddings dos modelos em lote (mais eficiente).
            model_text_vecs = provider.embed_texts([r.title for r in raws])

            # Achata TODAS as imagens de todos os modelos num único batch e
            # guarda o intervalo (span) de cada modelo para reagrupar depois.
            flat_urls: list[str | None] = []
            spans: list[tuple[int, int]] = []
            for r in raws:
                urls = list(r.image_urls) or ([r.thumbnail_url] if r.thumbnail_url else [])
                spans.append((len(flat_urls), len(flat_urls) + len(urls)))
                flat_urls.extend(urls)
            flat_img_vecs = provider.embed_image_urls(flat_urls)

            for idx, (raw, m_text) in enumerate(zip(raws, model_text_vecs)):
                start, end = spans[idx]
                img_vecs = [v for v in flat_img_vecs[start:end] if v]
                # embedding representativo do modelo (primeira imagem válida)
                m_img = img_vecs[0] if img_vecs else None
                # 1) upsert do modelo
                model = session.scalars(
                    select(Model3D).where(
                        Model3D.platform == raw.platform,
                        Model3D.external_id == raw.external_id,
                    )
                ).first()
                if model is None:
                    model = Model3D(platform=raw.platform, external_id=raw.external_id)
                    session.add(model)

                model.title = raw.title
                model.creator = raw.creator
                model.thumbnail_url = raw.thumbnail_url
                model.source_url = raw.source_url
                model.is_paid = raw.is_paid
                model.price_brl = raw.price_brl
                model.downloads = raw.downloads
                model.rating = raw.rating

                # 2) classificação de licença (título/descrição alimentam a flag de IP)
                verdict = classify_license(
                    raw.platform, raw.license_raw, raw.title, raw.description
                )
                model.license_tier = verdict.tier.value
                model.license_raw = verdict.raw
                model.license_reason = verdict.reason
                model.possible_protected_ip = verdict.possible_protected_ip
                model.license_checked_at = datetime.now(timezone.utc)

                session.flush()  # garante model.id
                _store_embedding(session, "model", model.id, "text", m_text)
                _store_embedding(session, "model", model.id, "image", m_img)

                # 3) score por cosseno. VISUAL = MAIOR similaridade entre a foto
                # do produto e QUALQUER imagem do modelo (cobre ângulos/renders).
                if prod_img_vec and img_vecs:
                    visual = max(cosine(prod_img_vec, v) for v in img_vecs)
                else:
                    visual = None
                text = cosine(prod_text_vec, m_text) if (prod_text_vec and m_text) else None
                result = combine(visual=visual, text=text)

                # 4) upsert do match
                match = session.scalars(
                    select(ProductModelMatch).where(
                        ProductModelMatch.product_id == product.id,
                        ProductModelMatch.model_id == model.id,
                    )
                ).first()
                if match is None:
                    match = ProductModelMatch(product_id=product.id, model_id=model.id)
                    session.add(match)
                match.visual_score = result.visual_score
                match.text_score = result.text_score
                match.feature_score = result.feature_score
                match.final_score = result.final_score
                match.match_level = int(result.level)
                count += 1

        session.commit()
        return count
    finally:
        session.close()
