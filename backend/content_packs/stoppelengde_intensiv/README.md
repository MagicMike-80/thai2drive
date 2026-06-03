# Content Pack: Stoppelengde Intensiv

Hard questions about stopping distance, braking distance, reaction distance,
and related hazards. Designed to make Thai2Drive's exam mode harder than
the real Statens vegvesen test.

---

## Folder structure

```
stoppelengde_intensiv/
├── questions_no_th_en.json   ← 30 questions, all three languages
├── images/                   ← place question images here
│   ├── q001.png
│   ├── q002.png
│   └── ...
└── README.md                 ← this file
```

---

## Image naming convention

Name each image after the question ID it belongs to:

| Question ID | Image filename |
|-------------|----------------|
| stop_001    | q001.png       |
| stop_002    | q002.png       |
| stop_003    | q003.png       |
| ...         | ...            |
| stop_030    | q030.png       |

Use `.png` for diagrams and `.jpg` for photographs.
Recommended size: **800 × 600 px minimum**, 16:9 or 4:3 ratio.

---

## How to connect an image to a question

1. Add the image file to `images/` (e.g. `q001.png`)
2. Open `questions_no_th_en.json`
3. Find the question with the matching `id`
4. Set the `"image"` field to the filename:

```json
{
  "id": "stop_001",
  "image": "q001.png",
  ...
}
```

The import script will look for the file at
`content_packs/stoppelengde_intensiv/images/<filename>`.

Leave `"image": ""` for questions that have no image yet.

---

## Topic coverage (30 questions)

| Topic                        | IDs               | Count |
|------------------------------|-------------------|-------|
| Reaction distance            | stop_001–004      | 4     |
| Braking distance             | stop_005–008      | 4     |
| Stopping distance            | stop_009–012      | 4     |
| Effect of doubled speed      | stop_013–015      | 3     |
| Wet / icy / dark roads       | stop_016–021      | 6     |
| Moose / children / pedestrians | stop_022–024    | 3     |
| Mobile phone distraction     | stop_025–026      | 2     |
| Fatigue and alcohol          | stop_027–028      | 2     |
| Safe following distance      | stop_029–030      | 2     |

All 30 questions are tagged `difficulty: hard` and `exam_boost`.

---

## How to import into MongoDB

**Do NOT run this yet — review the questions and add images first.**

When ready, use the import script (to be created):

```bash
cd backend
python import_content_pack.py --pack stoppelengde_intensiv --dry-run
# review output, then:
python import_content_pack.py --pack stoppelengde_intensiv
```

The script will:
1. Read `questions_no_th_en.json`
2. Convert each question to the Thai2Drive v2 question schema
3. Upload images to the media store and fill in `bildeUrl`
4. Insert or upsert into the `questions` collection
5. Skip questions that already exist (by `id`)

---

## Schema mapping

Each question in this pack maps to the database schema as follows:

```
Pack field          → DB field
─────────────────────────────────────────────────────────
id                  → id
category            → category
difficulty          → difficulty
image               → bildeUrl  (after upload)
question_no         → question.no
question_th         → question.th
question_en         → question.en
options_no[0..3]    → options[0..3].text.no
options_th[0..3]    → options[0..3].text.th
options_en[0..3]    → options[0..3].text.en
correct_index       → correctOptionId  (0→A, 1→B, 2→C, 3→D)
explanation_no      → explanation.no
explanation_th      → explanation.th
explanation_en      → explanation.en
```

`options[i].id` is set automatically: index 0 → "A", 1 → "B", 2 → "C", 3 → "D".
