"""
PDF P&ID Inventory Builder — 3-stage pipeline.

Stage 1: Text extraction
    PyMuPDF → list of Span (text, x, y, w, h, size) for every text span on the page.

Stage 2: Tag recognition + instrument-code decoding
    Regex over each span → TagHit (tag, plant_area, instrument_code, category).
    Instrument code encodes equipment type directly (HV → valve, P → pump, etc.)
    so we don't need CAD block names or layer names.

Stage 3a: Tiled spatial clustering (algorithmic, fast)
    Divide the page into an N×M grid of overlapping tiles.
    Within each tile: cluster nearby spans around tag seeds.
    A cluster = one instrument/equipment position on the drawing.
    Nearby non-tag text becomes the description.

Stage 3b: Tiled AI extraction (Claude vision, covers what regex misses)
    Each tile is rendered as a PNG image and sent to Claude.
    Claude identifies tags, equipment types, and descriptions directly from
    the image — works even when text is drawn as outlines (GOR) or scanned
    (KSD/ETP2) where Stage 2 finds nothing.
    AI results are merged with Stage 2 regex results; regex wins on overlap
    (deterministic over probabilistic where we have signal).

Output: dict matching pid_inventory.json schema so downstream
        hierarchy and SAP export stages work unchanged.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None  # type: ignore


# ---------------------------------------------------------------------------
# Instrument-code → inventory category mapping
# ---------------------------------------------------------------------------

# Manual / isolation valves
_VALVE_CODES = {
    "HV", "XV", "V", "KV", "NV", "BV", "GV", "MV", "SDV", "BDV", "PCV",
}

# Control / regulating valves (driven by a positioner/actuator)
_CTRL_VALVE_CODES = {
    "FV", "PV", "TV", "LV", "EV", "PDV", "CV", "AV",
}

# Transmitters
_INSTR_CODES = {
    "PT", "LT", "FT", "TT", "AT", "DT",
    "PI", "LI", "FI", "TI", "AI",
    "PC", "LC", "FC", "TC", "AC",
    "TE", "FE", "LE", "PE",
    "PS", "LS", "FS",
    "JBI", "CB", "EC", "CC", "CP", "BI", "PDI", "PDT", "PDIT",
}

# L4xx = agitator (Valmet convention); other L = level instrument
_AGITATOR_L_RE = re.compile(r"^L(4\d{2})$", re.I)


def _instr_code_category(code: str) -> str:
    """Map an instrument/equipment code to a pid_inventory category."""
    c = code.upper()
    if c == "P":
        return "pumps"
    if c == "T":
        return "tanks"
    if c in _VALVE_CODES:
        return "valves"
    if c in _CTRL_VALVE_CODES:
        return "control_valves"
    if c in _INSTR_CODES:
        return "instruments"
    if c == "L":
        return "instruments"  # resolved to agitator later if L4xx range
    if c.startswith("M"):
        return "motors"
    return "other"


def _kind_for_category(cat: str) -> str:
    if cat in ("pumps", "tanks", "motors"):
        return "equipment"
    if cat in ("valves", "control_valves"):
        return "valve"
    if cat == "instruments":
        return "instrument"
    return "equipment"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Span:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    size: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass
class TagHit:
    raw: str            # original text that matched
    tag: str            # normalised tag (upper, no extra spaces)
    plant_area: str     # e.g. "35-15"
    code: str           # instrument code e.g. "HV"
    seq: str            # sequence digits e.g. "5031"
    category: str       # "valves", "pumps", etc.
    span: Span


@dataclass
class Cluster:
    tag_hit: TagHit
    label_spans: list[Span] = field(default_factory=list)

    @property
    def x(self) -> float:
        return self.tag_hit.span.cx

    @property
    def y(self) -> float:
        return self.tag_hit.span.cy

    @property
    def description(self) -> str:
        parts = [s.text.strip() for s in self.label_spans if s.text.strip()]
        # Exclude the tag itself and very short noise strings
        filtered = [p for p in parts if p != self.tag_hit.tag and len(p) > 1]
        return "; ".join(filtered[:4]) if filtered else ""


# ---------------------------------------------------------------------------
# Stage 1 — Text extraction
# ---------------------------------------------------------------------------

TAG_RE = re.compile(
    r"""
    (?<!\w)                          # not preceded by word char
    (\d{2}-\d{2})                    # plant area e.g. 35-15
    [-\s]?                           # optional separator
    ([A-Z]{1,4})                     # instrument code  e.g. HV
    [-\s]?                           # optional separator
    (\d{3,4})                        # sequence digits  e.g. 5031
    (?!\w)                           # not followed by word char
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Line-number tags (pipe specs) — we classify separately, not as instruments
LINE_TAG_RE = re.compile(
    r"^\d{2}-\d{2}-\d{3,4}(-[A-Z]{1,5}(-\d+)?(-[A-Z0-9]+)*)?$", re.I
)


def extract_spans(pdf_path: Path) -> tuple[list[Span], fitz.Rect]:
    """Stage 1: extract all text spans with position from page 0.

    Uses two passes:
    1. get_text("words") — word-level, most reliable for tag extraction across PDFs.
    2. get_text("dict") — span-level, catches multi-word strings in a single run
       that words() may split (e.g. equipment descriptions).
    Deduplicates by text+position so we don't double-count.
    """
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is required — pip install pymupdf")

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    page_rect = page.rect
    page_h = page_rect.height

    spans: list[Span] = []
    seen: set[tuple] = set()

    def _add(txt: str, b: tuple, size: float = 8.0) -> None:
        txt = txt.strip()
        if not txt:
            return
        key = (txt, round(b[0], 1), round(b[1], 1))
        if key in seen:
            return
        seen.add(key)
        # Store in raw mediabox coordinates — consistent regardless of rotation.
        # Clustering uses only relative distances so the orientation doesn't matter.
        spans.append(
            Span(
                text=txt,
                x0=b[0],
                y0=b[1],
                x1=b[2],
                y1=b[3],
                size=size,
            )
        )

    # Pass 1: word-level without clip — covers the full mediabox including
    # pages with page.rotation (where page.rect != mediabox).
    for w in page.get_text("words"):
        _add(w[4], (w[0], w[1], w[2], w[3]))

    # Pass 2: span-level — catches multi-word label strings in a single run
    # (e.g. "REJECT COMPACTOR 1") that Pass 1 splits into separate words.
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for sp in line.get("spans", []):
                _add(sp["text"], sp["bbox"], size=sp.get("size", 8.0))

    return spans, page_rect


# ---------------------------------------------------------------------------
# Stage 2 — Tag recognition
# ---------------------------------------------------------------------------

def find_tag_hits(spans: list[Span]) -> list[TagHit]:
    """Stage 2: find all instrument-tag bearing spans."""
    hits: list[TagHit] = []
    seen: set[str] = set()

    for sp in spans:
        for m in TAG_RE.finditer(sp.text):
            plant_area = m.group(1).upper()
            code = m.group(2).upper()
            seq = m.group(3)
            tag = f"{plant_area}-{code}-{seq}"

            # Skip line-number style (pipe specs, not instruments)
            if LINE_TAG_RE.match(tag):
                continue

            cat = _instr_code_category(code)
            # Resolve L4xx → agitator
            if code == "L" and _AGITATOR_L_RE.match(f"L{seq}"):
                cat = "agitators"

            if tag in seen:
                continue
            seen.add(tag)

            hits.append(
                TagHit(
                    raw=m.group(0),
                    tag=tag,
                    plant_area=plant_area,
                    code=code,
                    seq=seq,
                    category=cat,
                    span=sp,
                )
            )
    return hits


# ---------------------------------------------------------------------------
# Stage 3 — Tiled spatial clustering
# ---------------------------------------------------------------------------

def _content_bounds(spans: list[Span]) -> tuple[float, float, float, float]:
    """Bounding box of all span centroids — used for tiling."""
    if not spans:
        return 0.0, 0.0, 1.0, 1.0
    xs = [s.cx for s in spans]
    ys = [s.cy for s in spans]
    return min(xs), min(ys), max(xs), max(ys)


def _tile_bounds(
    content_box: tuple[float, float, float, float],
    col: int,
    row: int,
    cols: int,
    rows: int,
    overlap: float = 0.15,
) -> tuple[float, float, float, float]:
    """Return (x0, y0, x1, y1) in content coordinate space."""
    bx0, by0, bx1, by1 = content_box
    pw = bx1 - bx0
    ph = by1 - by0

    tw = pw / cols
    th = ph / rows

    ox = tw * overlap
    oy = th * overlap

    x0 = max(bx0, bx0 + col * tw - ox)
    x1 = min(bx1, bx0 + (col + 1) * tw + ox)
    y0 = max(by0, by0 + row * th - oy)
    y1 = min(by1, by0 + (row + 1) * th + oy)

    return x0, y0, x1, y1


def _spans_in_tile(
    spans: list[Span],
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> list[Span]:
    return [
        s for s in spans
        if x0 <= s.cx <= x1 and y0 <= s.cy <= y1
    ]


def _dist(a: Span, b: Span) -> float:
    return math.hypot(a.cx - b.cx, a.cy - b.cy)


def cluster_tile(
    tile_spans: list[Span],
    tag_hits_in_tile: list[TagHit],
    max_dist: float = 80.0,
) -> list[Cluster]:
    """
    For each tag seed in the tile, collect nearby spans as description labels.
    A span claimed by a closer seed won't be reused (greedy, nearest-first).
    """
    if not tag_hits_in_tile:
        return []

    # Sort seeds by x so processing is deterministic
    seeds = sorted(tag_hits_in_tile, key=lambda h: h.span.cx)

    # Pool of non-seed spans available for association
    seed_spans = {id(h.span) for h in seeds}
    pool = [s for s in tile_spans if id(s) not in seed_spans]

    clusters: list[Cluster] = []
    claimed: set[int] = set()

    for hit in seeds:
        near = [
            s for s in pool
            if id(s) not in claimed and _dist(hit.span, s) <= max_dist
        ]
        # Sort by distance so we take closest labels first
        near.sort(key=lambda s: _dist(hit.span, s))
        # Cap at 6 labels to avoid pulling in neighbouring instrument text
        labels = near[:6]
        for s in labels:
            claimed.add(id(s))
        clusters.append(Cluster(tag_hit=hit, label_spans=labels))

    return clusters


def build_clusters(
    spans: list[Span],
    tag_hits: list[TagHit],
    page_rect: Any,
    cols: int = 4,
    rows: int = 3,
    max_dist: float = 80.0,
    overlap: float = 0.15,
) -> list[Cluster]:
    """Stage 3: tile the page and cluster within each tile."""
    # Use actual span positions for tiling — handles rotated pages where
    # page.rect doesn't match the mediabox coordinate space.
    content_box = _content_bounds(spans)

    all_clusters: list[Cluster] = []
    seen_tags: set[str] = set()

    for row in range(rows):
        for col in range(cols):
            x0, y0, x1, y1 = _tile_bounds(
                content_box, col, row, cols, rows, overlap
            )
            tile_spans = _spans_in_tile(spans, x0, y0, x1, y1)
            tile_hits = [
                h for h in tag_hits
                if x0 <= h.span.cx <= x1 and y0 <= h.span.cy <= y1
                and h.tag not in seen_tags
            ]

            clusters = cluster_tile(tile_spans, tile_hits, max_dist=max_dist)

            for c in clusters:
                if c.tag_hit.tag not in seen_tags:
                    seen_tags.add(c.tag_hit.tag)
                    all_clusters.append(c)

    return all_clusters


# ---------------------------------------------------------------------------
# Stage 3b — AI tile extraction (Claude vision via Bedrock)
# ---------------------------------------------------------------------------

_AI_TILE_PROMPT = """\
You are reading a tile cropped from a P&ID (Piping and Instrumentation Diagram).

TASK: Extract every instrument and equipment function tag that is clearly visible in this image tile.

WHAT A TAG LOOKS LIKE:
Tags always start with a two-digit plant area, a dash, and another two digits:
  36-43L001      compact: area=36-43, code=L, seq=001
  36-43P501      compact: area=36-43, code=P, seq=501
  35-15-HV-5031  dashed: area=35-15, code=HV, seq=5031
  55-34-LV-550   dashed: area=55-34, code=LV, seq=550

Common equipment codes:
  P = pump              T = tank / vessel          L = level / agitator (L4xx range)
  HV, XV, V = valve     FV, TV, PV, LV = control valve
  PT, LT, FT, TT = transmitter    PI, LI, FI, TI = indicator

DO NOT INCLUDE:
  - Drawing number or title block reference numbers (e.g. PCSG028671, STOD206344)
  - Pipe line numbers / pipe specs (e.g. 36-43-001-BDS-32, 001-20)
  - Revision numbers or dates
  - Grid reference letters/numbers (A, B, 1, 2 etc.)
  - Dimension labels or general numbers without a plant-area prefix

Return ONLY a valid JSON array (no markdown fences, no explanation):
[
  {{"tag": "36-43L001", "equipment_type": "instrument", "description": "brief nearby label"}},
  {{"tag": "36-43P501", "equipment_type": "pump", "description": "BENTONITE PUMP 1"}},
  ...
]

Rules:
- Only include tags you can clearly read — do NOT guess
- Keep the exact characters you see — do NOT add or remove dashes
- Return [] if no instrument/equipment tags are visible in this tile
"""


def _render_tile_png(
    page: Any,
    col: int,
    row: int,
    cols: int,
    rows: int,
    dpi: int = 150,
    overlap: float = 0.15,
) -> bytes:
    """Render one tile as PNG bytes.

    Uses page.rect (display coordinates, already accounts for page rotation)
    so the image always looks correct regardless of the PDF's rotation attribute.
    """
    pr = page.rect
    tw = pr.width / cols
    th = pr.height / rows
    ox, oy = tw * overlap, th * overlap

    x0 = max(0.0, col * tw - ox)
    x1 = min(pr.width, (col + 1) * tw + ox)
    y0 = max(0.0, row * th - oy)
    y1 = min(pr.height, (row + 1) * th + oy)

    clip = fitz.Rect(x0, y0, x1, y1)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip, colorspace=fitz.csGRAY)
    return pix.tobytes("png")


def _ai_extract_tile(
    image_bytes: bytes,
    tile_text: str,
    model_id: str,
    region: str,
) -> list[dict[str, Any]]:
    """Send one tile image to Claude and return a list of tag dicts."""
    try:
        import boto3
    except ImportError:
        return []

    prompt = _AI_TILE_PROMPT.format(tile_text=tile_text.strip() or "(none)")

    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        messages=[{
            "role": "user",
            "content": [
                {"image": {"format": "png", "source": {"bytes": image_bytes}}},
                {"text": prompt},
            ],
        }],
        inferenceConfig={"maxTokens": 2000, "temperature": 0},
    )

    raw = "\n".join(
        b["text"]
        for b in response.get("output", {}).get("message", {}).get("content", [])
        if "text" in b
    ).strip()

    # Pull out the first JSON array from the response
    m = re.search(r"\[.*?\]", raw, re.DOTALL)
    if not m:
        return []
    try:
        return json.loads(m.group(0))
    except Exception:
        return []


def _ai_type_to_category(equipment_type: str) -> str:
    t = (equipment_type or "").lower().replace("_", " ").replace("-", " ")
    if "control" in t or t in ("fv", "tv", "pv", "lv", "ev", "pdv"):
        return "control_valves"
    if "valve" in t:
        return "valves"
    if "pump" in t:
        return "pumps"
    if "tank" in t or "vessel" in t:
        return "tanks"
    if "agitator" in t or "mixer" in t:
        return "agitators"
    if "motor" in t:
        return "motors"
    if "instrument" in t or "transmit" in t or "indicator" in t or "controller" in t:
        return "instruments"
    # Fall back to instrument code in the tag if we can decode it
    return "instruments"


def ai_build_inventory_tiles(
    pdf_path: Path,
    cols: int = 4,
    rows: int = 3,
    dpi: int = 150,
    overlap: float = 0.15,
    model_id: str = "eu.anthropic.claude-sonnet-4-6",
    region: str = "eu-west-2",
) -> dict[str, Any]:
    """
    AI-only path: render each tile → Claude vision → merge across tiles.

    Works even when the PDF has no extractable text (GOR outline-text, KSD raster).
    Also runs Stage 1+2 and merges regex hits (regex wins on overlap).
    """
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is required — pip install pymupdf")

    doc = fitz.open(str(pdf_path))
    page = doc[0]

    # Stage 1+2 — text extraction and regex tags (may return nothing for GOR/KSD)
    spans, page_rect = extract_spans(pdf_path)
    regex_hits = find_tag_hits(spans)
    regex_tags: set[str] = {h.tag for h in regex_hits}

    # Index spans by their tile for building tile_text context
    content_box = _content_bounds(spans) if spans else (0, 0, 1, 1)

    ai_results: list[dict[str, Any]] = []
    seen_tags: set[str] = set()

    # Seed seen_tags with regex hits so AI won't duplicate them
    for h in regex_hits:
        seen_tags.add(h.tag)

    print(f"  Sending {cols * rows} tiles to AI ({cols}×{rows}) …")

    for row in range(rows):
        for col in range(cols):
            # Render tile in display coordinates (handles rotated pages)
            image_bytes = _render_tile_png(page, col, row, cols, rows, dpi, overlap)

            # Build text context from spans in this tile (mediabox coords)
            tile_box = _tile_bounds(content_box, col, row, cols, rows, overlap)
            tile_spans = _spans_in_tile(spans, *tile_box)
            tile_text = "\n".join(s.text for s in tile_spans if len(s.text) > 1)[:800]

            raw_items = _ai_extract_tile(image_bytes, tile_text, model_id, region)

            for item in raw_items:
                raw_tag = str(item.get("tag") or "").strip().upper()
                if not raw_tag or raw_tag in seen_tags:
                    continue

                # Normalise compact format (e.g. 36-44P501 → 36-44-P-501)
                m = TAG_RE.search(raw_tag)
                if m:
                    tag = f"{m.group(1).upper()}-{m.group(2).upper()}-{m.group(3)}"
                else:
                    tag = raw_tag  # keep as-is if it doesn't match

                if tag in seen_tags:
                    continue
                seen_tags.add(tag)

                cat = _ai_type_to_category(item.get("equipment_type", ""))
                # Try to decode from instrument code if AI category is generic
                code_m = re.search(r"^\d{2}-\d{2}-?([A-Z]{1,4})-?\d{3,4}$", tag)
                if code_m and cat == "instruments":
                    cat = _instr_code_category(code_m.group(1))

                area_m = re.match(r"^(\d{2}-\d{2})", tag)
                plant_area = area_m.group(1) if area_m else ""

                ai_results.append({
                    "tag": tag,
                    "plant_area": plant_area,
                    "equipment_type": item.get("equipment_type", ""),
                    "category": cat,
                    "description": (item.get("description") or "").strip(),
                    "source": "ai",
                    "confidence": "medium",
                })

            print(f"    tile({col},{row}): {len(raw_items)} AI tags", end="")
            new_this_tile = sum(1 for r in ai_results if r.get("source") == "ai")
            print()

    # Merge: regex clusters first (high confidence), then AI-only additions
    clusters = build_clusters(spans, regex_hits, page_rect, cols=cols, rows=rows)

    by_cat: dict[str, list[dict]] = defaultdict(list)
    functions: list[dict] = []

    for idx, c in enumerate(clusters):
        cat = c.tag_hit.category
        comp = _cluster_to_component(c, idx)
        fn = _cluster_to_function(c, idx)
        by_cat[cat].append(comp)
        functions.append(fn)

    # Append AI-only tags (not found by regex)
    for idx, item in enumerate(ai_results):
        tag = item["tag"]
        cat = item["category"]
        h = _handle(tag, idx)
        comp = {
            "component_type": cat,
            "tag": tag,
            "plant_area": item["plant_area"],
            "instrument_code": "",
            "handle": h,
            "layer": f"AI-{cat.upper()}",
            "x": 0.0, "y": 0.0, "z": 0.0,
            "position": "0.0,0.0,0.0",
            "description": item["description"] or None,
            "source": "ai",
            "confidence": "medium",
        }
        fn = {
            "kind": _kind_for_category(cat),
            "category": cat,
            "block_name": None,
            "handle": h,
            "layer": f"AI-{cat.upper()}",
            "x": 0.0, "y": 0.0, "z": 0.0,
            "description": item["description"] or None,
            "nearby_tags": tag,
            "confidence": "medium",
            "function": tag,
            "source": "ai",
        }
        by_cat[cat].append(comp)
        functions.append(fn)

    regex_count = len(clusters)
    ai_count = len(ai_results)

    return {
        "source": "pdf+ai",
        "pdf_path": str(pdf_path),
        "page_size": {"width": page_rect.width, "height": page_rect.height},
        "tile_grid": {"cols": cols, "rows": rows},
        "span_count": len(spans),
        "tag_count": len(regex_hits),
        "regex_functions": regex_count,
        "ai_functions": ai_count,
        "tanks": by_cat.get("tanks", []),
        "process_equipment": by_cat.get("process_equipment", []),
        "agitators": by_cat.get("agitators", []),
        "pumps": by_cat.get("pumps", []),
        "motors": by_cat.get("motors", []),
        "valves": by_cat.get("valves", []),
        "control_valves": by_cat.get("control_valves", []),
        "instruments": by_cat.get("instruments", []),
        "other": by_cat.get("other", []),
        "functions": functions,
    }




# ---------------------------------------------------------------------------
# Pure-AI PDF inventory — vision-only, no regex, no text extraction
# ---------------------------------------------------------------------------

_PURE_AI_TILE_PROMPT = """You are reading a tile from an engineering P&ID (Piping and Instrumentation Diagram).

Your job: for every instrument/equipment function tag visible in this image, extract the tag, its
position, what it connects to, and any specs. Be exhaustive — do NOT skip any tag.

== WHAT A VALID TAG LOOKS LIKE ==
A function tag ALWAYS has:
  1. A plant-area prefix: two groups of 2 digits separated by a dash  (e.g., 36-43  or  35-39)
  2. Followed immediately by an equipment/instrument code  (e.g., L  P  T  HV  FT  HS)
  3. Followed by a 3-4 digit sequence number  (e.g., 001  501  601  5031)

Valid examples:
  36-43L001      (area 36-43, code L, seq 001)
  36-43-P-501    (area 36-43, code P, seq 501)
  35-39T601      (area 35-39, code T, seq 601)
  36-43-HV-019   (area 36-43, code HV, seq 019)

Common codes: P=pump  T=tank  L=process_equipment  HV/XV/KV=valve  FV/PV/LV/TV=control_valve
              FT/PT/LT/TT/PI/LI/HS/SC/WIQ/LAH/FAL=instrument  M=motor

== FOR EACH TAG, PROVIDE ==
  tag            — the full tag string exactly as written (e.g., "36-43-P-501")
  equipment_type — one of: pump / tank / valve / control_valve / instrument / motor / process_equipment
  description    — human-readable label or name visible near the tag bubble (e.g., "bentonite silo 150 M3")
  x_frac         — horizontal position of the tag bubble center as a fraction of this tile's width  (0.0=left edge, 1.0=right edge)
  y_frac         — vertical position of the tag bubble center as a fraction of this tile's height (0.0=top edge, 1.0=bottom edge)
  connected_to   — list of OTHER full tag strings you can see are directly connected to this tag by
                   a pipe line or signal/control line within this image. Use [] if none visible.
  specs          — dict of measurable specs written near this tag, e.g.:
                   {"volume": "150 M3", "flow": "250-500 lpm", "pressure": "4 bar", "size": "DN80",
                    "temperature": "80 C", "material": "SS316"}
                   Use {} if no specs are visible.

== CRITICAL RULES ==
1. EVERY tag MUST start with the two-digit-dash-two-digit area prefix (e.g., 36-43 or 35-39).
   If you see only "HV-007" WITHOUT the prefix, skip it entirely.

2. Do NOT include pipe/line numbers — these look like: 36-43-050-SS-3  or  36-43-025-WWL
   (3-digit size + pipe class letters after the area). Exclude them.

3. Do NOT include revision marks, sheet numbers, title block text, or bare area codes.

4. Include a tag cut off at the tile edge only if you can clearly read the full prefix + code + seq.

Return ONLY a JSON array — no markdown fences, no explanation:
[
  {
    "tag": "36-43-T-601",
    "equipment_type": "tank",
    "description": "bentonite silo 150 M3",
    "x_frac": 0.72,
    "y_frac": 0.35,
    "connected_to": ["36-43-P-501", "36-43-HV-023"],
    "specs": {"volume": "150 M3"}
  },
  {
    "tag": "36-43-P-501",
    "equipment_type": "pump",
    "description": "",
    "x_frac": 0.55,
    "y_frac": 0.60,
    "connected_to": ["36-43-T-601", "36-43-HV-023"],
    "specs": {"flow": "250-500 lpm", "pressure": "4 bar"}
  }
]

Return [] if no valid function tags (with area prefix) are visible in this tile.
"""


def _render_tile_png_pure(
    page: Any,
    col: int,
    row: int,
    cols: int,
    rows: int,
    dpi: int = 200,
    overlap: float = 0.15,
) -> tuple[bytes, float, float, float, float]:
    """Render one tile as PNG at given DPI. Returns (png_bytes, x0, y0, x1, y1) in page.rect space."""
    pr = page.rect
    tw = pr.width / cols
    th = pr.height / rows
    ox, oy = tw * overlap, th * overlap

    x0 = max(0.0, col * tw - ox)
    x1 = min(pr.width, (col + 1) * tw + ox)
    y0 = max(0.0, row * th - oy)
    y1 = min(pr.height, (row + 1) * th + oy)

    clip = fitz.Rect(x0, y0, x1, y1)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip, colorspace=fitz.csGRAY)
    return pix.tobytes("png"), x0, y0, x1, y1


def _ai_extract_tile_pure(
    image_bytes: bytes,
    tile_x0: float,
    tile_y0: float,
    tile_x1: float,
    tile_y1: float,
    model_id: str,
    region: str,
) -> list[dict[str, Any]]:
    """Send one tile image to Claude and return enriched tag dicts with absolute PDF coordinates."""
    try:
        import boto3
    except ImportError:
        return []

    client = boto3.client("bedrock-runtime", region_name=region)
    try:
        response = client.converse(
            modelId=model_id,
            messages=[{
                "role": "user",
                "content": [
                    {"image": {"format": "png", "source": {"bytes": image_bytes}}},
                    {"text": _PURE_AI_TILE_PROMPT},
                ],
            }],
            inferenceConfig={"maxTokens": 4000, "temperature": 0},
        )
    except Exception as exc:
        print(f"    [bedrock error] {exc}")
        return []

    raw = "\n".join(
        b["text"]
        for b in response.get("output", {}).get("message", {}).get("content", [])
        if "text" in b
    ).strip()

    # Extract outermost JSON array using balanced bracket scan
    start = raw.find("[")
    if start == -1:
        return []
    depth, end = 0, -1
    for i, ch in enumerate(raw[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        return []
    try:
        items = json.loads(raw[start:end + 1])
    except Exception:
        return []

    tw = tile_x1 - tile_x0
    th = tile_y1 - tile_y0
    for item in items:
        xf = float(item.get("x_frac") or 0.5)
        yf = float(item.get("y_frac") or 0.5)
        item["_x"] = tile_x0 + xf * tw
        item["_y"] = tile_y0 + yf * th
        item.setdefault("connected_to", [])
        item.setdefault("specs", {})
    return items


def _normalise_tag(raw: str) -> str:
    """Normalise a tag to NN-NN-CODE-NNN form.

    Accepts: "36-43L001", "36-43-L-001", "36 43 L 001", etc.
    Returns: "36-43-L-001" (canonical dashed form).
    Falls back to the upper-cased input if pattern does not match.
    """
    raw = raw.strip().upper()
    m = TAG_RE.search(raw)
    if m:
        area = m.group(1).upper()
        code = m.group(2).upper()
        seq = m.group(3)
        return f"{area}-{code}-{seq}"
    return raw


def ai_build_inventory_pure(
    pdf_path: Path,
    cols: int = 4,
    rows: int = 3,
    dpi: int = 200,
    overlap: float = 0.15,
    model_id: str = "eu.anthropic.claude-sonnet-4-6",
    region: str = "eu-west-2",
) -> dict[str, Any]:
    """
    Pure-AI PDF inventory: render each tile as PNG -> Claude vision -> merge.

    No regex, no text extraction — works for any PDF including scanned / outline-text.
    Each tile image is sent to Claude with a focused prompt asking it to read every
    function tag visible. Results are normalised and deduplicated across tiles.

    Returns a dict matching the pid_inventory.json schema (same as build_inventory).
    """
    if fitz is None:
        raise ImportError("PyMuPDF (fitz) is required — pip install pymupdf")

    doc = fitz.open(str(pdf_path))
    page = doc[0]
    page_rect = page.rect

    ai_results: list[dict[str, Any]] = []
    seen_tags: set[str] = set()
    tile_stats: list[str] = []

    total_tiles = cols * rows
    print(f"  Pure-AI: {total_tiles} tiles ({cols}x{rows}) at {dpi} DPI ...")

    for row in range(rows):
        for col in range(cols):
            image_bytes, tx0, ty0, tx1, ty1 = _render_tile_png_pure(page, col, row, cols, rows, dpi, overlap)
            raw_items = _ai_extract_tile_pure(image_bytes, tx0, ty0, tx1, ty1, model_id, region)

            new_in_tile = 0
            for item in raw_items:
                raw_tag = str(item.get("tag") or "").strip()
                if not raw_tag:
                    continue
                tag = _normalise_tag(raw_tag)
                if not tag or tag in seen_tags:
                    continue

                # Reject: tag must start with NN-NN- prefix (plant area)
                if not re.match(r"^\d{2}-\d{2}-", tag):
                    continue

                # Reject: pipe/line specs (area-3digits-PIPECLASS pattern)
                if re.match(r"^\d{2}-\d{2}-\d{3}[^A-Z]", tag) or re.match(r"^\d{2}-\d{2}-\d{3}$", tag):
                    continue

                # Reject: bare area codes without equipment code+seq
                if not re.search(r"-[A-Z]{1,4}-\d{3}", tag):
                    continue

                seen_tags.add(tag)
                new_in_tile += 1

                eq_type = str(item.get("equipment_type") or "").lower()
                cat = _ai_type_to_category(eq_type)
                code_m = re.match(r"^\d{2}-\d{2}-?([A-Z]{1,4})-?\d{3,4}$", tag)
                if code_m:
                    decoded = _instr_code_category(code_m.group(1))
                    if decoded != "other":
                        cat = decoded

                area_m = re.match(r"^(\d{2}-\d{2})", tag)
                plant_area = area_m.group(1) if area_m else ""

                # Normalise connected_to tags
                raw_conn = item.get("connected_to") or []
                connections = [_normalise_tag(t) for t in raw_conn if str(t).strip()]
                connections = [t for t in connections if re.match(r"^\d{2}-\d{2}-", t)]

                ai_results.append({
                    "tag": tag,
                    "plant_area": plant_area,
                    "equipment_type": eq_type,
                    "category": cat,
                    "description": (item.get("description") or "").strip(),
                    "x": item.get("_x", 0.0),
                    "y": item.get("_y", 0.0),
                    "connected_to": connections,
                    "specs": item.get("specs") or {},
                    "source": "ai_pure",
                    "confidence": "medium",
                    "tile": f"{col},{row}",
                })

            stat = f"({col},{row}): {len(raw_items)} seen, {new_in_tile} new"
            tile_stats.append(stat)
            print(f"    tile {stat}")

    # Assemble inventory in pid_inventory.json schema
    by_cat: dict[str, list[dict]] = defaultdict(list)
    functions: list[dict] = []

    for idx, item in enumerate(ai_results):
        tag = item["tag"]
        cat = item["category"]
        h = _handle(tag, idx)

        x, y = item.get("x") or 0.0, item.get("y") or 0.0
        comp = {
            "component_type": cat,
            "tag": tag,
            "plant_area": item["plant_area"],
            "instrument_code": "",
            "handle": h,
            "layer": f"AI-PURE-{cat.upper()}",
            "x": x, "y": y, "z": 0.0,
            "position": f"{x:.2f},{y:.2f},0.0",
            "description": item["description"] or None,
            "connected_to": item.get("connected_to") or [],
            "specs": item.get("specs") or {},
            "source": "ai_pure",
            "confidence": "medium",
        }
        fn = {
            "kind": _kind_for_category(cat),
            "category": cat,
            "block_name": None,
            "handle": h,
            "layer": f"AI-PURE-{cat.upper()}",
            "x": x, "y": y, "z": 0.0,
            "description": item["description"] or None,
            "nearby_tags": tag,
            "connected_to": item.get("connected_to") or [],
            "specs": item.get("specs") or {},
            "confidence": "medium",
            "function": tag,
            "source": "ai_pure",
        }
        by_cat[cat].append(comp)
        functions.append(fn)

    # Build global connection edge list (deduplicated, sorted pair as key)
    edge_set: set[tuple[str, str]] = set()
    for item in ai_results:
        src = item["tag"]
        for dst in item.get("connected_to") or []:
            edge = tuple(sorted([src, dst]))
            edge_set.add(edge)
    connections = [{"from": a, "to": b} for a, b in sorted(edge_set)]

    print(f"  Pure-AI total: {len(functions)} unique tags, {len(connections)} connections from {total_tiles} tiles")

    return {
        "source": "pdf+ai_pure",
        "pdf_path": str(pdf_path),
        "page_size": {"width": page_rect.width, "height": page_rect.height},
        "tile_grid": {"cols": cols, "rows": rows, "dpi": dpi},
        "span_count": 0,
        "tag_count": 0,
        "regex_functions": 0,
        "ai_functions": len(functions),
        "tile_stats": tile_stats,
        "connections": connections,
        "tanks": by_cat.get("tanks", []),
        "process_equipment": by_cat.get("process_equipment", []),
        "agitators": by_cat.get("agitators", []),
        "pumps": by_cat.get("pumps", []),
        "motors": by_cat.get("motors", []),
        "valves": by_cat.get("valves", []),
        "control_valves": by_cat.get("control_valves", []),
        "instruments": by_cat.get("instruments", []),
        "other": by_cat.get("other", []),
        "functions": functions,
    }

# ---------------------------------------------------------------------------
# Inventory assembly — match pid_inventory.json schema
# ---------------------------------------------------------------------------

def _handle(tag: str, idx: int) -> str:
    """Stable short handle for a PDF-derived entity."""
    h = hashlib.md5(tag.encode()).hexdigest()[:6].upper()
    return f"PDF-{h}"


def _position_str(x: float, y: float) -> str:
    return f"{x:.6f},{y:.6f},0.000000"


def _cluster_to_function(c: Cluster, idx: int) -> dict[str, Any]:
    hit = c.tag_hit
    return {
        "kind": _kind_for_category(hit.category),
        "category": hit.category,
        "block_name": None,
        "handle": _handle(hit.tag, idx),
        "layer": f"PDF-{hit.category.upper()}",
        "x": c.x,
        "y": c.y,
        "z": 0.0,
        "description": c.description or None,
        "nearby_tags": hit.tag,
        "confidence": "medium",
        "function": hit.tag,
        "source": "pdf",
    }


def _cluster_to_component(c: Cluster, idx: int) -> dict[str, Any]:
    hit = c.tag_hit
    return {
        "component_type": hit.category,
        "tag": hit.tag,
        "plant_area": hit.plant_area,
        "instrument_code": hit.code,
        "handle": _handle(hit.tag, idx),
        "layer": f"PDF-{hit.category.upper()}",
        "x": c.x,
        "y": c.y,
        "z": 0.0,
        "position": _position_str(c.x, c.y),
        "description": c.description or None,
        "source": "pdf",
        "confidence": "medium",
    }


def build_inventory(
    pdf_path: Path,
    cols: int = 4,
    rows: int = 3,
    max_dist: float = 80.0,
) -> dict[str, Any]:
    """
    Full 3-stage pipeline.  Returns a dict matching pid_inventory.json schema.
    """
    # Stage 1
    spans, page_rect = extract_spans(pdf_path)

    # Stage 2
    tag_hits = find_tag_hits(spans)

    # Stage 3
    clusters = build_clusters(
        spans, tag_hits, page_rect, cols=cols, rows=rows, max_dist=max_dist
    )

    # Assemble inventory
    by_cat: dict[str, list[dict]] = defaultdict(list)
    functions: list[dict] = []

    for idx, c in enumerate(clusters):
        cat = c.tag_hit.category
        by_cat[cat].append(_cluster_to_component(c, idx))
        functions.append(_cluster_to_function(c, idx))

    return {
        "source": "pdf",
        "pdf_path": str(pdf_path),
        "page_size": {"width": page_rect.width, "height": page_rect.height},
        "tile_grid": {"cols": cols, "rows": rows},
        "span_count": len(spans),
        "tag_count": len(tag_hits),
        "tanks": by_cat.get("tanks", []),
        "process_equipment": by_cat.get("process_equipment", []),
        "agitators": by_cat.get("agitators", []),
        "pumps": by_cat.get("pumps", []),
        "motors": by_cat.get("motors", []),
        "valves": by_cat.get("valves", []),
        "control_valves": by_cat.get("control_valves", []),
        "instruments": by_cat.get("instruments", []),
        "other": by_cat.get("other", []),
        "functions": functions,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    import os

    from dwg_reader.config import DEFAULT_MODEL_ID

    parser = argparse.ArgumentParser(
        description="Build a P&ID inventory from a vector PDF"
    )
    parser.add_argument("pdf", type=Path, help="Input PDF path")
    parser.add_argument("--out", type=Path, default=None, help="Output JSON path")
    parser.add_argument("--cols", type=int, default=4, help="Tile columns (default 4)")
    parser.add_argument("--rows", type=int, default=3, help="Tile rows (default 3)")
    parser.add_argument("--max-dist", type=float, default=80.0,
                        help="Max clustering distance in PDF units (default 80)")
    parser.add_argument("--ai", action="store_true",
                        help="Enable Stage 3b: send each tile to Claude vision for additional tag extraction")
    parser.add_argument("--ai-only", action="store_true",
                        help="Use AI tile path only (for GOR/KSD PDFs with no extractable text)")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--region", default=None)
    parser.add_argument("--aws-profile", default=os.environ.get("AWS_PROFILE", "foundrydev"))
    parser.add_argument("--dpi", type=int, default=150,
                        help="Tile render DPI for AI mode (default 150)")
    parser.add_argument("--summary", action="store_true",
                        help="Print summary table only, not full JSON")
    args = parser.parse_args()

    region = args.region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "eu-west-2"
    if args.aws_profile:
        os.environ["AWS_PROFILE"] = args.aws_profile

    if args.ai_only:
        inv = ai_build_inventory_pure(
            args.pdf,
            cols=args.cols,
            rows=args.rows,
            dpi=args.dpi,
            model_id=args.model_id,
            region=region,
        )
    elif args.ai:
        inv = ai_build_inventory_tiles(
            args.pdf,
            cols=args.cols,
            rows=args.rows,
            dpi=args.dpi,
            model_id=args.model_id,
            region=region,
        )
    else:
        inv = build_inventory(args.pdf, cols=args.cols, rows=args.rows, max_dist=args.max_dist)

    if args.summary:
        print(f"\nPDF: {args.pdf.name}")
        print(f"Page: {inv['page_size']['width']:.0f} × {inv['page_size']['height']:.0f} pt")
        print(f"Tiles: {inv['tile_grid']['cols']} × {inv['tile_grid']['rows']}")
        print(f"Text spans: {inv['span_count']}")
        print(f"Regex tags: {inv['tag_count']}  |  AI additions: {inv.get('ai_functions', '-')}")
        print(f"Total functions: {len(inv['functions'])}")
        print()
        cats = ["pumps", "tanks", "agitators", "valves", "control_valves", "instruments", "motors", "other"]
        for cat in cats:
            items = inv.get(cat, [])
            if items:
                sample = [i["tag"] for i in items[:5]]
                print(f"  {cat:16s}: {len(items):4d}   {sample}")
        print()
        print("Functions (first 15):")
        for fn in inv["functions"][:15]:
            src = fn.get("source", "?")
            print(f"  [{src:5s}] {fn['function']:25s}  {fn['category']:16s}  {fn['description'] or ''!r}")
    else:
        out = args.out or args.pdf.with_suffix(".pid_inventory.json")
        out.write_text(json.dumps(inv, indent=2, ensure_ascii=False))
        print(f"Written: {out}  ({len(inv['functions'])} functions, {inv.get('ai_functions',0)} from AI)")


if __name__ == "__main__":
    main()
