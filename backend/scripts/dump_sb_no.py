# -*- coding: utf-8 -*-
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent / "image_audit"
d = json.loads((HERE / "studiebok_prod.json").read_text(encoding="utf-8"))
out = HERE / "sb_no"
out.mkdir(exist_ok=True)
for c in d:
    if c["order"] == 1:
        continue
    f = out / "ch{:02d}.html".format(c["order"])
    f.write_text("TITLE: " + c["title_no"] + "\n" + c["content_no"], encoding="utf-8")
print("skrevet kap 2-15 til", out)
