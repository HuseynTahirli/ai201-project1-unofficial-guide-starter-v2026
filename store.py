"""
Stages 3 and 4 of the pipeline: embedding chunks and retrieving them.

Three things in here are worth knowing about, because they'd quietly break the
rest of the project if they were wrong:

1. The Chroma collection is created with cosine distance, explicitly. Chroma
   defaults to squared L2, and the 0.6 threshold the course uses is calibrated
   against cosine. Getting this wrong makes every distance number meaningless.

2. `search` returns the distance alongside each chunk. Milestone 4 has you
   compare distances, so they have to be visible.

3. The embedding model is the one Chroma bundles, not one loaded through
   `sentence-transformers`. It is the same model — `all-MiniLM-L6-v2`, 384
   dimensions — but it arrives as an ONNX build from Chroma's own CDN, so the
   install needs neither PyTorch nor a reachable Hugging Face. See `_embedder`.

4. `search` is hybrid. It runs the embedding search and a BM25 keyword search
   on the same question and merges the two rankings with reciprocal rank
   fusion. Fusion decides the *order*; every result still carries its real
   cosine distance, so the relevance gate and its 0.6-style cutoff mean
   exactly what they meant before. A chunk that only BM25 found gets its
   distance computed from its stored embedding.
"""

import os
import re
import shutil
from dataclasses import dataclass

# Must be set BEFORE chromadb is imported. Without it, some Chroma versions
# print "Failed to send telemetry event ..." on every single call — which looks
# exactly like a real error, isn't one, and cost a previous cohort a lot of
# confused help-channel messages.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb  # noqa: E402
import numpy as np  # noqa: E402
from rank_bm25 import BM25Okapi  # noqa: E402

import config
from chunker import Chunk


@dataclass
class Result:
    """One retrieved chunk and how far it was from the question."""

    text: str
    source: str
    label: str
    distance: float   # LOWER IS BETTER. 0.3 is close, 0.9 is unrelated.
    produced_by: str
    score: float = 0.0  # fused rank score, HIGHER IS BETTER. Orders results only.


_model = None

# Hybrid search. Each retriever contributes its best CANDIDATE_POOL chunks (or
# 4 x top_k, if that's bigger), and reciprocal rank fusion scores a chunk as
# the sum of 1 / (RRF_K + rank) over the rankings it appears in. 60 is the
# value from the original RRF paper and the usual default.
CANDIDATE_POOL = 20
RRF_K = 60

# The model Chroma bundles. Anything else in config.EMBEDDING_MODEL means
# "fetch that one from Hugging Face instead" — see `_embedder`.
BUNDLED_MODEL = "all-MiniLM-L6-v2"


class _OnnxEmbedder:
    """
    Chroma's built-in embedder, wrapped to look like the other two.

    Chroma's embedding functions are called directly and hand back numpy
    arrays. The rest of this file wants `.encode(texts)`, so the adapter lives
    here rather than making every caller care which embedder it got.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        self._ef = ONNXMiniLM_L6_V2()

    def encode(self, texts, show_progress_bar: bool = False):
        return [vector.tolist() for vector in self._ef(list(texts))]


def _sentence_transformer(name: str):
    """
    The escape hatch: any model that isn't the bundled one.

    Unit 2's "try a second embedding model" stretch option comes through here,
    and so does anything you set `EMBEDDING_MODEL` to. This path *does* need
    `sentence-transformers` and a reachable Hugging Face, neither of which the
    default install has — which is the whole point of the default install.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            f"config.EMBEDDING_MODEL is set to {name!r}, which isn't the model "
            f"Chroma bundles ({BUNDLED_MODEL!r}), so it has to be downloaded "
            f"from Hugging Face.\n"
            f"Install the optional dependency first:\n"
            f"    pip install 'sentence-transformers>=3.4,<3.5'\n"
            f"Or set EMBEDDING_MODEL back to {BUNDLED_MODEL!r}."
        ) from exc

    return SentenceTransformer(name)


def _embedder():
    """
    Load the embedding model once and keep it.

    First call is slow — it downloads about 80 MB. That's why setup happens
    before class.
    """
    global _model

    if _model is not None:
        return _model

    # Used only by this repo's own smoke test, which runs where no model can be
    # downloaded at all. Never set this yourself.
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        from _smoke_embedder import FakeEmbedder

        _model = FakeEmbedder()
    elif config.EMBEDDING_MODEL == BUNDLED_MODEL:
        _model = _OnnxEmbedder()
    else:
        _model = _sentence_transformer(config.EMBEDDING_MODEL)

    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Turn text into vectors. Runs on your machine, costs no API quota."""
    vectors = _embedder().encode(texts, show_progress_bar=False)
    # sentence-transformers and the smoke stand-in return something with a
    # .tolist(); _OnnxEmbedder has already done that conversion itself.
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


def build_index(
    chunks: list[Chunk],
    corpus: str | None = None,
    variant: str = "default",
) -> int:
    """
    Embed every chunk and store it.

    `variant` lets you keep more than one index of the same corpus at the same
    time. In unit 2, when you compare two chunking strategies, index the second
    one as variant="v2" and you can query both instead of deleting the first
    and starting over.
    """
    name = config.collection_name(corpus, variant)
    client = _client()

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name,
        # ⚠️ Do not remove. Chroma defaults to squared L2, and every distance
        # number in this course assumes cosine.
        metadata={"hnsw:space": "cosine"},
    )

    batch = 256
    for start in range(0, len(chunks), batch):
        window = chunks[start : start + batch]
        collection.add(
            ids=[f"{c.source}#{c.index}" for c in window],
            documents=[c.text for c in window],
            embeddings=embed([c.text for c in window]),
            metadatas=[
                {"source": c.source, "index": c.index, "produced_by": c.produced_by}
                for c in window
            ],
        )

    return len(chunks)


def _tokenize(text: str) -> list[str]:
    """Lowercased word tokens for BM25."""
    return re.findall(r"\w+", text.lower())


def _cosine_distance(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(1.0 - a.dot(b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search(
    question: str,
    top_k: int | None = None,
    corpus: str | None = None,
    variant: str = "default",
) -> list[Result]:
    """
    Retrieve the chunks that best match a question, by meaning and by keyword.

    Runs the embedding search and BM25 over the same collection, fuses the two
    rankings with reciprocal rank fusion, and returns the top_k best-fused
    first. Each result keeps its cosine distance to the question, which is
    what the relevance gate checks.
    """
    top_k = top_k or config.TOP_K
    name = config.collection_name(corpus, variant)

    try:
        collection = _client().get_collection(name)
    except Exception as exc:
        raise RuntimeError(
            f"No index called '{name}'. Run `python app.py index` first."
        ) from exc

    total = collection.count()
    if total == 0:
        return []
    pool = min(max(CANDIDATE_POOL, top_k * 4), total)

    # Semantic ranking.
    query_vector = embed([question])
    raw = collection.query(query_embeddings=query_vector, n_results=pool)
    semantic_ids = raw["ids"][0]
    distances = dict(zip(semantic_ids, raw["distances"][0]))

    # Keyword ranking. BM25 needs the whole collection to compute term rarity.
    everything = collection.get(include=["documents", "metadatas"])
    all_ids = everything["ids"]
    by_id = {
        cid: (text, meta)
        for cid, text, meta in zip(
            all_ids, everything["documents"], everything["metadatas"]
        )
    }
    bm25 = BM25Okapi([_tokenize(text) for text in everything["documents"]])
    keyword_scores = bm25.get_scores(_tokenize(question))
    keyword_order = sorted(
        range(len(all_ids)), key=lambda i: keyword_scores[i], reverse=True
    )
    # A score of 0 or less means no query term matched usefully; that is not
    # a keyword hit, so it doesn't get a rank.
    keyword_ids = [all_ids[i] for i in keyword_order[:pool] if keyword_scores[i] > 0]

    # Reciprocal rank fusion.
    fused: dict[str, float] = {}
    for ranking in (semantic_ids, keyword_ids):
        for rank, cid in enumerate(ranking, start=1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (RRF_K + rank)
    top_ids = sorted(fused, key=fused.get, reverse=True)[:top_k]

    # Chunks only BM25 found have no distance yet; compute it from the stored
    # embedding so every result carries a real cosine distance for the gate.
    missing = [cid for cid in top_ids if cid not in distances]
    if missing:
        stored = collection.get(ids=missing, include=["embeddings"])
        for cid, vector in zip(stored["ids"], stored["embeddings"]):
            distances[cid] = _cosine_distance(query_vector[0], vector)

    results: list[Result] = []
    for cid in top_ids:
        text, meta = by_id[cid]
        results.append(
            Result(
                text=text,
                source=str(meta.get("source", "unknown")),
                label=f"{meta.get('source', 'unknown')}#{meta.get('index', 0)}",
                distance=float(distances[cid]),
                produced_by=str(meta.get("produced_by", "unknown")),
                score=fused[cid],
            )
        )
    return results


def index_exists(corpus: str | None = None, variant: str = "default") -> bool:
    """Is there an index here to search, without searching it?

    `serve.py`'s health check asks this. It deliberately does not embed
    anything: loading the embedding model takes 80 MB and a few seconds, and a
    health check that heavy is a health check nobody can afford to call.
    """
    try:
        collection = _client().get_collection(config.collection_name(corpus, variant))
        return collection.count() > 0
    except Exception:
        return False


def reset():
    """Delete every index. Occasionally the fastest way out of a mess."""
    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)
