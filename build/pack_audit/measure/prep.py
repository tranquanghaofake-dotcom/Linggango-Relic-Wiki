"""Write the plan for kubejs/server_scripts/lgw_measure.js: which items to measure in game.
Usage: prep.py OUT.json [--test] [--extra | --third] [--auto --stop]
  copy OUT.json to the game's kubejs/lgw_items.json (or kubejs/lgw_test_items.json with --test: 5 weapons, 2 sets, 10 items);
  --auto starts it 200 ticks after a dedicated server loads, --stop shuts the server down when done
--extra writes the second plan instead (kubejs/lgw_extra_items.json, /kubejs custom_command lgw_measure_extra): the weapons the
  first run marked "grows" (patches/gear_measure.json), to swing at several targets, and every curio of the wiki, worn one at a time;
  with --test as well: 2 of those weapons and 6 curios, for kubejs/lgw_extra_test_items.json (/kubejs custom_command lgw_measure_extra_test).
attrs: every gear item and curio of the wiki; melee: every weapon with a melee score; sets: every armor set with its pieces' slots.
The result (kubejs/lgw_measure.json) goes back into build/patches/ the way gear_runtime.json does."""
import json, sys, pathlib, re
H = pathlib.Path(__file__).resolve().parents[2]
s = (H / "src" / "gear_data.js").read_text(encoding="utf-8"); d = json.JSONDecoder()
GE, i = d.raw_decode(s, s.index("[", s.index("GE="))); GS, _ = d.raw_decode(s, s.index("[", s.index("GS=", i)))
c = (H / "src" / "data.js").read_text(encoding="utf-8"); D, _ = d.raw_decode(c, c.index("["))
SLOT = {"HELMET": "HEAD", "CHESTPLATE": "CHEST", "LEGGINGS": "LEGS", "BOOTS": "FEET"}
by = {g["id"]: g for g in GE}
plan = {"hits": 3, "stop": "--stop" in sys.argv, "auto": "--auto" in sys.argv,
        "attrs": sorted({g["id"] for g in GE} | {x["id"] for x in D}),
        "melee": sorted(g["id"] for g in GE if g["k"] == "melee" or g.get("dmg") is not None),
        "sets": [{"k": x["k"], "p": [[p, SLOT.get(by[p].get("sl"), "CHEST")] for p in x["p"] if p in by]} for x in GS]}
if "--test" in sys.argv:
    melee = [g["id"] for g in GE if g.get("fx") and g.get("dmg") is not None][:3] + ["minecraft:diamond_sword", "minecraft:netherite_axe"]
    plan.update(attrs=melee + ["minecraft:diamond_chestplate", "minecraft:netherite_helmet"] + plan["attrs"][:6], melee=melee,
                sets=[x for x in plan["sets"] if x["k"] in ("minecraft:diamond", "minecraft:netherite")][:2] or plan["sets"][:2])
if "--third" in sys.argv:
    # third run (/kubejs custom_command lgw_measure_third): shots from every bow, crossbow and thrown weapon (guns fire through their
    # mods' own key packets, left out), the target-dependent weapons again with the pig turned toward and away, and the curios that
    # cancelled their one test hit, hit ten times
    M = json.loads((H / "patches" / "gear_measure.json").read_text(encoding="utf-8"))
    CMx = json.loads((H / "patches" / "curio_measure.json").read_text(encoding="utf-8"))["curios"]
    GUN = re.compile(r"Gun|Rifle|Pistol|Shotgun|Revolver|Blaster|Railgun|Musket|Launcher")
    ranged = sorted(g["id"] for g in GE if g["k"] == "ranged" and not any(GUN.search(c) for c in g.get("cls") or []))
    grows = sorted(k for k, v in M["items"].items() if v.get("st") in ("grows", "pct") or v.get("swx"))
    blocks = sorted(k for k, v in CMx.items() if any(x != "fall" for x in v.get("neg") or []))
    if "--test" in sys.argv:
        ranged = [x for x in ("minecraft:bow", "minecraft:crossbow", "minecraft:trident") if x in {g["id"] for g in GE}] or ranged[:3]
        grows = [x for x in grows if x == "brutality:shadowstep"] or grows[:1]
        blocks = [x for x in blocks if x in ("morerelics:opal_necklace", "meetyourfight:ace_of_iron")] or blocks[:2]
    plan = {"hits": 3, "stop": "--stop" in sys.argv, "auto": "--auto" in sys.argv, "ranged": ranged, "grows": grows, "blocks": blocks}
    json.dump(plan, open(sys.argv[1], "w"), indent=0)
    print(len(ranged), "shooters,", len(grows), "weapons turned,", len(blocks), "blocking curios ->", sys.argv[1]); sys.exit()
if "--extra" in sys.argv:
    M = json.loads((H / "patches" / "gear_measure.json").read_text(encoding="utf-8"))
    grows = sorted(k for k, v in M["items"].items() if v.get("st") == "grows")
    cur = sorted(x["id"] for x in D)
    if "--test" in sys.argv:
        grows = [g for g in grows if g in ("lethality:nightfall", "brutality:shadowstep")] or grows[:2]
        cur = [x for x in ("armageddon_mod:pendant_of_convergence", "armageddon_mod:anhk_aegis", "terramity:ultra_sniffer_fur") if x in cur] + cur[:3]
    plan = {"hits": 3, "stop": "--stop" in sys.argv, "auto": "--auto" in sys.argv, "grows": grows, "curios": cur}
    json.dump(plan, open(sys.argv[1], "w"), indent=0)
    print(len(grows), "weapons to re-measure,", len(cur), "curios ->", sys.argv[1]); sys.exit()
json.dump(plan, open(sys.argv[1], "w"), indent=0)
print(len(plan["attrs"]), "items,", len(plan["melee"]), "melee,", len(plan["sets"]), "sets ->", sys.argv[1])
