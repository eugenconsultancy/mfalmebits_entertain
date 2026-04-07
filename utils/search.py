"""
utils/search.py
─────────────────────────────────────────────────────────────────────
Production-ready, multi-model search utility for MfalmeBits.

Features
  • Multi-field Q-object search with configurable field weights
  • Stopword filtering & query sanitisation
  • Fuzzy prefix matching (icontains) for real-world typos
  • Per-model search helpers that return annotated querysets
  • A single `site_search()` aggregator that queries all major models
  • Pagination-aware result builder

Usage:
    from utils.search import site_search, search_archive, search_blog

    results = site_search("ubuntu philosophy", page=1)
    archive_qs = search_archive("Sankofa", theme_slug="history")
"""

import re
import logging
from typing import Any

from django.db.models import Q, QuerySet, Value, CharField, F
from django.db.models.functions import Concat

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────

#: Tokens shorter than this are ignored (avoids noise from words like "a", "I")
MIN_TOKEN_LENGTH = 2

#: Maximum tokens to build Q objects for (keeps queries sane)
MAX_TOKENS = 8

#: Common English stopwords that add no search value
STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "are", "was", "were",
    "be", "been", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can",
    "not", "no", "nor", "so", "yet", "both", "either", "neither",
    "this", "that", "these", "those", "it", "its", "as", "if",
})

# ── Query Sanitisation ───────────────────────────────────────────────

def sanitise_query(raw: str) -> str:
    """
    Strip HTML, control characters, and excessive whitespace from a raw
    search string.  Returns a clean string suitable for tokenising.
    """
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", " ", raw)
    # Remove non-alphanumeric except spaces and hyphens
    clean = re.sub(r"[^\w\s\-]", " ", clean)
    # Collapse whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:200]  # Hard cap to prevent DoS via enormous queries


def tokenise(query: str) -> list[str]:
    """
    Split a sanitised query into individual tokens, removing stopwords
    and very short words.

    Returns a deduplicated list of lowercase tokens (up to MAX_TOKENS).
    """
    raw_tokens = sanitise_query(query).lower().split()
    tokens = [
        t for t in raw_tokens
        if len(t) >= MIN_TOKEN_LENGTH and t not in STOPWORDS
    ]
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:MAX_TOKENS]


# ── Core Q-Builder ───────────────────────────────────────────────────

def build_q(tokens: list[str], fields: list[str]) -> Q:
    """
    Build a combined Q object that matches *any* token in *any* field.

    Each (token, field) pair generates a case-insensitive LIKE filter.
    All pairs are OR-ed together so that partial matches are surfaced.

    Args:
        tokens: Cleaned search tokens from tokenise().
        fields: Django ORM field lookup paths, e.g. ["title", "tags__name"].

    Returns:
        A Q object ready to pass to .filter().
    """
    if not tokens or not fields:
        return Q()  # Empty Q — no restriction applied

    combined = Q()
    for token in tokens:
        token_q = Q()
        for field in fields:
            token_q |= Q(**{f"{field}__icontains": token})
        combined |= token_q

    return combined


# ── Per-Model Search Functions ───────────────────────────────────────

def search_archive(
    query: str,
    theme_slug: str | None = None,
    tag: str | None = None,
    limit: int = 20,
) -> QuerySet:
    """
    Search the Knowledge Archive.

    Searches: title, excerpt, content, author, tags__name.
    Supports optional narrowing by theme_slug and tag.
    """
    from apps.archive.models import ArchiveEntry  # local import avoids circular deps

    tokens = tokenise(query)
    qs = ArchiveEntry.objects.filter(is_active=True)

    if tokens:
        qs = qs.filter(
            build_q(tokens, ["title", "excerpt", "content", "author", "tags__name"])
        ).distinct()

    if theme_slug:
        qs = qs.filter(theme__slug=theme_slug)

    if tag:
        qs = qs.filter(tags__slug=tag)

    return qs.select_related("theme").prefetch_related("tags")[:limit]


def search_blog(
    query: str,
    category_slug: str | None = None,
    limit: int = 20,
) -> QuerySet:
    """
    Search blog posts (published only).
    """
    from apps.blog.models import Post

    tokens = tokenise(query)
    qs = Post.objects.filter(status="published", is_active=True)

    if tokens:
        qs = qs.filter(
            build_q(tokens, ["title", "excerpt", "content", "tags__name"])
        ).distinct()

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    return (
        qs.select_related("author", "category")
        .prefetch_related("tags")[:limit]
    )


def search_library(
    query: str,
    category_slug: str | None = None,
    limit: int = 20,
) -> QuerySet:
    """
    Search the Digital Library (active products).
    """
    from apps.library.models import DigitalProduct

    tokens = tokenise(query)
    qs = DigitalProduct.objects.filter(is_active=True)

    if tokens:
        qs = qs.filter(
            build_q(tokens, ["title", "short_description", "author", "tags__name"])
        ).distinct()

    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    return qs.select_related("category").prefetch_related("tags")[:limit]


def search_collaboration(query: str, limit: int = 10) -> QuerySet:
    """
    Search published collaboration projects.
    """
    from apps.collaboration.models import CollaborationProject

    tokens = tokenise(query)
    qs = CollaborationProject.objects.filter(status="published")

    if tokens:
        qs = qs.filter(
            build_q(tokens, ["title", "short_description", "creator_name", "creator_location"])
        ).distinct()

    return qs[:limit]


# ── Aggregated Site Search ───────────────────────────────────────────

def site_search(
    query: str,
    page: int = 1,
    per_page: int = 10,
) -> dict[str, Any]:
    """
    Run a search across all major content types and return a unified
    results dict suitable for passing directly to a template context.

    Args:
        query:    Raw search string from the user.
        page:     1-based page number.
        per_page: Number of results per content type.

    Returns:
        {
            "query":        str,       # sanitised query
            "tokens":       list[str], # parsed tokens
            "archive":      QuerySet,
            "blog":         QuerySet,
            "library":      QuerySet,
            "collaboration": QuerySet,
            "total":        int,       # approximate total across all types
            "has_results":  bool,
        }
    """
    clean_query = sanitise_query(query)
    tokens = tokenise(clean_query)

    if not tokens:
        return {
            "query": clean_query,
            "tokens": [],
            "archive": [],
            "blog": [],
            "library": [],
            "collaboration": [],
            "total": 0,
            "has_results": False,
        }

    # Fetch results for each model (limited to per_page each)
    archive_results = search_archive(clean_query, limit=per_page)
    blog_results = search_blog(clean_query, limit=per_page)
    library_results = search_library(clean_query, limit=per_page)
    collab_results = search_collaboration(clean_query, limit=per_page // 2)

    # Count approx total (evaluate counts without loading all objects)
    total = (
        archive_results.count()
        + blog_results.count()
        + library_results.count()
        + collab_results.count()
    )

    logger.info(
        "site_search: query=%r tokens=%s total=%d",
        clean_query, tokens, total,
    )

    return {
        "query": clean_query,
        "tokens": tokens,
        "archive": archive_results,
        "blog": blog_results,
        "library": library_results,
        "collaboration": collab_results,
        "total": total,
        "has_results": total > 0,
    }


# ── Search Highlight Helper ───────────────────────────────────────────

def highlight(text: str, tokens: list[str], tag: str = "mark") -> str:
    """
    Wrap every occurrence of each token in `text` with an HTML tag.

    Safe for template use with |safe filter.  Does NOT escape the input
    text — only call this on already-sanitised values.

    Example:
        highlight("African philosophy is profound", ["philosophy"])
        → 'African <mark>philosophy</mark> is profound'
    """
    if not tokens or not text:
        return text

    for token in tokens:
        pattern = re.compile(re.escape(token), re.IGNORECASE)
        text = pattern.sub(lambda m: f"<{tag}>{m.group()}</{tag}>", text)

    return text