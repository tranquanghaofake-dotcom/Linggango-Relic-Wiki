"""Stage 1 of the gear pipeline: the extraction table (gear_table.json, build/gear/gear_data.py output) is the starting point.
The old generator also scored items; src/gear.js scores everything now, so stale `sc` fields are dropped."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent

def load():
    T = json.loads((H / "gear_table.json").read_text(encoding="utf-8"))
    for x in T["GE"] + T["GS"]: x.pop("sc", None)
    return {"GE": T["GE"], "GS": T["GS"],
            "GNS": json.loads((H / "gear_names.json").read_text(encoding="utf-8")),   # mod namespace -> display name
            "IC": json.loads((H / "gear_icons.json").read_text(encoding="utf-8"))}    # item id -> 64px icon (base64 PNG)
