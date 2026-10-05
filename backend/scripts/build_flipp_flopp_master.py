"""Build the web game's 50-card pack from Michael-approved yes/no content."""

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


LANGUAGES = ("no", "th", "en")
CATEGORIES = {"vikeplikt", "plassering", "se", "stopp", "myndighet"}
ANSWERS = {
    True: {"no": "Ja", "th": "ใช่", "en": "Yes"},
    False: {"no": "Nei", "th": "ไม่ใช่", "en": "No"},
}
IMAGE_NAME = re.compile(r"^[A-Za-z0-9_.-]+\.(?:jpg|jpeg|png|webp)$", re.IGNORECASE)


def _localized(value, field, card_id):
    if not isinstance(value, dict):
        raise ValueError(f"Kort {card_id}: {field} må ha no/th/en")
    result = {}
    for lang in LANGUAGES:
        text = value.get(lang)
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Kort {card_id}: {field}.{lang} mangler")
        result[lang] = text.strip()
    return result


def build_cards(document, asset_dir):
    if not isinstance(document, dict) or document.get("total_cards") != 50:
        raise ValueError("Kilden må angi nøyaktig 50 kort")
    source_cards = document.get("cards")
    if not isinstance(source_cards, list) or len(source_cards) != 50:
        raise ValueError("Kilden må inneholde nøyaktig 50 kort")

    result = []
    ids = set()
    counts = {category: 0 for category in CATEGORIES}
    for card in source_cards:
        if not isinstance(card, dict):
            raise ValueError("Alle kort må være objekter")
        card_id = card.get("id")
        if type(card_id) is not int or card_id not in range(1, 51) or card_id in ids:
            raise ValueError(f"Ugyldig eller duplisert kort-ID: {card_id}")
        if card.get("source_card_id") != card_id:
            raise ValueError(f"Kort {card_id}: feil kilde-ID")
        if card.get("fasit_godkjent_av_michael") is not True:
            raise ValueError(f"Kort {card_id}: fasit er ikke godkjent av Michael")
        truth = card.get("answer")
        if type(truth) is not bool:
            raise ValueError(f"Kort {card_id}: Ja/Nei-fasit må være boolsk")
        category = card.get("category")
        if category not in CATEGORIES:
            raise ValueError(f"Kort {card_id}: ugyldig kategori")
        image = card.get("image")
        if not isinstance(image, str) or not IMAGE_NAME.fullmatch(image):
            raise ValueError(f"Kort {card_id}: bilde mangler eller har ugyldig filnavn")
        if not (asset_dir / image).is_file():
            raise ValueError(f"Kort {card_id}: bildefilen {image} finnes ikke")
        alt = _localized(card.get("alt"), "alt", card_id)
        statement = {}
        explanation = {}
        for lang in LANGUAGES:
            copy = card.get(lang)
            if not isinstance(copy, dict):
                raise ValueError(f"Kort {card_id}: {lang}-tekst mangler")
            statement[lang] = copy.get("statement")
            explanation[lang] = copy.get("explanation")
            if not isinstance(statement[lang], str) or not statement[lang].strip():
                raise ValueError(f"Kort {card_id}: {lang}.statement mangler")
            if not isinstance(explanation[lang], str) or not explanation[lang].strip():
                raise ValueError(f"Kort {card_id}: {lang}.explanation mangler")
            statement[lang] = statement[lang].strip()
            explanation[lang] = explanation[lang].strip()
        fagord = card.get("norwegian_fagord")
        reference = card.get("source")
        if not isinstance(fagord, str) or not fagord.strip():
            raise ValueError(f"Kort {card_id}: norsk fagord mangler")
        if not isinstance(reference, str) or not reference.strip():
            raise ValueError(f"Kort {card_id}: regelkilde mangler")

        ids.add(card_id)
        counts[category] += 1
        result.append({
            "id": f"master-{card_id}",
            "source_id": card_id,
            "category": category,
            "statement": statement,
            "truth": truth,
            "answer": ANSWERS[truth],
            "explanation": explanation,
            "alt": alt,
            "image": image,
            "fagord": fagord.strip(),
            "ref": reference.strip(),
            "approved_by_michael": True,
        })

    if ids != set(range(1, 51)) or any(count != 10 for count in counts.values()):
        raise ValueError("Kortene må dekke ID 1–50 og fem kategorier med ti kort hver")
    return sorted(result, key=lambda card: card["source_id"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "public_assets" / "flipp_flopp_master_50.json")
    args = parser.parse_args()
    try:
        cards = build_cards(json.loads(args.source.read_text(encoding="utf-8")), args.output.parent)
    except ValueError as exc:
        parser.error(str(exc))
    payload = json.dumps(cards, ensure_ascii=False, indent=2) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent, prefix=".flipp_flopp_master_", suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
        os.replace(temporary, args.output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(f"Bygget {len(cards)} godkjente Ja/Nei-kort: {args.output}")


if __name__ == "__main__":
    main()
