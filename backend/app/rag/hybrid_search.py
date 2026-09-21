"""Reciprocal Rank Fusion (RRF) za hibridnu pretragu.

RRF(d) = sum_i 1 / (k + rank_i(d)), gdje je k konstanta (obično 60).
Robusna metoda fuzije jer ne ovisi o skali pojedinačnih score-ova.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.rag.retriever import RetrievedChunk

RRF_K = 60


def reciprocal_rank_fusion(
    result_lists: list[list["RetrievedChunk"]], top_k: int = 5, k: int = RRF_K
) -> list["RetrievedChunk"]:
    scores: dict[int, float] = {}
    best_instance: dict[int, "RetrievedChunk"] = {}

    for results in result_lists:
        for rank, chunk in enumerate(results, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (k + rank)
            if chunk.chunk_id not in best_instance:
                best_instance[chunk.chunk_id] = chunk

    ranked_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)[:top_k]
    fused: list["RetrievedChunk"] = []
    for cid in ranked_ids:
        chunk = best_instance[cid]
        chunk.score = round(scores[cid], 6)
        fused.append(chunk)
    return fused
