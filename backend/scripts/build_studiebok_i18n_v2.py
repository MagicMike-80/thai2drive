# -*- coding: utf-8 -*-
"""Bygger content_packs/studiebok_i18n_v2.json.

Kombinerer prod-dumpen (scripts/image_audit/studiebok_prod.json) med
oversettelsesfilene i content_packs/studiebok_i18n_v2/src/.

Kapittel 1 har allerede th/en i prod og hoppes over.
Pakken inneholder KUN oversettelsesfeltene (title_th/title_en/content_th/content_en)
matchet på `order` — content_no og title_no skal aldri endres av importen.

Validerer at HTML-strukturen (tagger og klasser) matcher den norske kilden.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PROD = BASE / "scripts" / "image_audit" / "studiebok_prod.json"
SRC = BASE / "content_packs" / "studiebok_i18n_v2" / "src"
OUT = BASE / "content_packs" / "studiebok_i18n_v2.json"

TAG_RE = re.compile(r"<(/?)([a-z]+)((?:\s+[a-z-]+=\"[^\"]*\")*)\s*>", re.I)
CLASS_RE = re.compile(r'class="([^"]+)"')


def parse_file(path):
    text = path.read_text(encoding="utf-8").strip()
    lines = text.split("\n")
    if not lines[0].startswith("TITLE: "):
        raise ValueError("Mangler TITLE-linje: %s" % path.name)
    title = lines[0][len("TITLE: "):].strip()
    content = "\n".join(lines[1:]).strip()
    return title, content


def structure(html):
    """Teller tagger og klasser — for strukturmatching mot norsk kilde."""
    tags = Counter()
    classes = Counter()
    for m in TAG_RE.finditer(html):
        closing, tag, attrs = m.groups()
        if not closing:
            tags[tag.lower()] += 1
            for cm in CLASS_RE.finditer(attrs or ""):
                classes[cm.group(1)] += 1
    return tags, classes


def main():
    prod = json.loads(PROD.read_text(encoding="utf-8"))
    by_order = {ch["order"]: ch for ch in prod}

    updates = []
    warnings = []

    for order in range(2, 16):
        ch = by_order.get(order)
        if ch is None:
            print("FEIL: kapittel %d finnes ikke i prod-dumpen" % order)
            sys.exit(1)

        entry = {"order": order, "match_on": "order"}
        no_tags, no_classes = structure(ch.get("content_no", ""))

        for lang in ("en", "th"):
            path = SRC / ("ch%02d.%s.html" % (order, lang))
            if not path.exists():
                print("FEIL: mangler fil %s" % path.name)
                sys.exit(1)
            title, content = parse_file(path)
            if not title or not content:
                print("FEIL: tom tittel/innhold i %s" % path.name)
                sys.exit(1)
            entry["title_" + lang] = title
            entry["content_" + lang] = content

            tags, classes = structure(content)
            for cls in ("study-law", "study-tip"):
                if classes.get(cls, 0) != no_classes.get(cls, 0):
                    warnings.append(
                        "ch%02d %s: %s-antall %d (norsk: %d)"
                        % (order, lang, cls, classes.get(cls, 0), no_classes.get(cls, 0))
                    )
            for tag in ("ul", "ol", "li"):
                if tags.get(tag, 0) != no_tags.get(tag, 0):
                    warnings.append(
                        "ch%02d %s: <%s>-antall %d (norsk: %d)"
                        % (order, lang, tag, tags.get(tag, 0), no_tags.get(tag, 0))
                    )

        updates.append(entry)

    pack = {
        "pack": "studiebok_i18n_v2",
        "collection": "studiebok_chapters",
        "description": (
            "Thai + engelsk oversettelse av studiebok-kapittel 2-15. "
            "Match paa feltet 'order'. Sett KUN title_th, title_en, "
            "content_th, content_en. Roer ALDRI title_no/content_no. "
            "Kapittel 1 har allerede oversettelser og er ikke med."
        ),
        "fields_to_set": ["title_th", "title_en", "content_th", "content_en"],
        "chapters": updates,
    }

    OUT.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Skrev %s" % OUT)
    print("Kapitler: %d (order 2-15)" % len(updates))
    if warnings:
        print("\nADVARSLER (strukturavvik mot norsk kilde):")
        for w in warnings:
            print("  -", w)
    else:
        print("Strukturvalidering: OK — alle study-law/study-tip/lister matcher norsk kilde")

    # JSON-validering ved gjenlesing
    json.loads(OUT.read_text(encoding="utf-8"))
    print("JSON-validering: OK")


if __name__ == "__main__":
    main()
