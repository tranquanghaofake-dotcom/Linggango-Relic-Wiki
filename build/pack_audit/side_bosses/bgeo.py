"""GeckoLib side bosses: geometry, texture and idle animation from the mod jars, as records in the format of
patches/boss_models.json, so boss_portraits.html draws them like the Keepers. Usage: bgeo.py W JARS_DIR [boss|boss...]
→ W/sb_geo_in.json; then `node build/pack_audit/boss_portraits.js --in W/sb_geo_in.json --out W/sb_geo_out.json` and pack.py.
G: the geometry and texture picked by hand (the renderer chooses phase or variant textures in code). The animation file is
the one named like the geometry among those the model class names (getAnimationResource), else its only one, else the one
named like the geometry; the pose is its idle animation (the name ending in "idle", else the shortest one containing it; in a
file shared by several mobs only one naming this mob) at frame 0, or the rest pose when there is none (Iron's casters pose
their idle in code)."""
import json, sys, zipfile, glob, re, base64, io
from PIL import Image
W, JD = sys.argv[1], sys.argv[2]; ONLY = sys.argv[3].split("|") if len(sys.argv) > 3 else None
G = {"Draugr → Night Shade": ("soulsweapons/geo/entity/draugr_boss.geo.json", "soulsweapons/textures/entity/draugr_boss.png"),
     "Umvuthi": ("mowziesmobs/geo/umvuthi.geo.json", "mowziesmobs/textures/entity/umvuthi.png"),
     "Dead King": ("irons_spellbooks/geo/dead_king.geo.json", "irons_spellbooks/textures/entity/dead_king/dead_king.png"),
     "Returning Knight": ("soulsweapons/geo/entity/returning_knight.geo.json", "soulsweapons/textures/entity/returning_knight.png"),
     "Malkuth": ("fdbosses/bedrock/models/malkuth.geo.json", "fdbosses/textures/entities/malkuth/malkuth.png"),
     "Lich": ("bosses_of_mass_destruction/geo/lich.geo.json", "bosses_of_mass_destruction/textures/entity/lich.png"),
     "Super Sniffer": ("terramity/geo/super_sniffer.geo.json", "terramity/textures/entities/super_sniffer_base.png"),
     "Gundalf, Circe, Merlin (Shadow Wizards)": ("terramity/geo/gundalf.geo.json", "terramity/textures/entities/gundalf.png"),
     "Gauntlet": ("bosses_of_mass_destruction/geo/gauntlet.geo.json", "bosses_of_mass_destruction/textures/entity/gauntlet.png"),
     "Obsidilith": ("bosses_of_mass_destruction/geo/obsidilith.geo.json", "bosses_of_mass_destruction/textures/entity/obsidilith.png"),
     "Void Blossom": ("bosses_of_mass_destruction/geo/void_blossom.geo.json", "bosses_of_mass_destruction/textures/entity/void_blossom.png"),
     "Chesed": ("fdbosses/bedrock/models/chesed.geo.json", "fdbosses/textures/entities/chesed.png"),
     "Moonknight": ("soulsweapons/geo/entity/moonknight.geo.json", "soulsweapons/textures/entity/moonknight/moonknight_phase_1.png"),
     "Accursed Lord": ("soulsweapons/geo/entity/accursed_lord.geo.json", "soulsweapons/textures/entity/accursed_lord.png"),
     "Tyros (fire boss)": ("irons_spellbooks/geo/tyros.geo.json", "irons_spellbooks/textures/entity/fire_boss/tyros.png"),
     "Gob, King of Gnomes": ("terramity/geo/gob.geo.json", "terramity/textures/entities/gob.png"),
     "Trial Guardian": ("terramity/geo/trial_guardian.geo.json", "terramity/textures/entities/trial_guardian.png"),
     "Geburah": ("fdbosses/bedrock/models/geburah.geo.json", "fdbosses/textures/entities/geburah/geburah.png"),
     "Day Stalker": ("soulsweapons/geo/entity/day_stalker.geo.json", "soulsweapons/textures/entity/day_stalker.png"),
     "Night Prowler": ("soulsweapons/geo/entity/night_prowler.geo.json", "soulsweapons/textures/entity/night_prowler.png"),
     "Chaos Monarch": ("soulsweapons/geo/entity/chaos_monarch.geo.json", "soulsweapons/textures/entity/chaos_monarch.png"),
     "The Nightwarden": ("traveloptics/geo/nightwarden.geo.json", "traveloptics/textures/models/entity/nightwarden/nightwarden.png"),
     "Virtue": ("terramity/geo/virtue.geo.json", "terramity/textures/entities/virtue.png"),
     "Ultra Sniffer": ("terramity/geo/ultra_sniffer.geo.json", "terramity/textures/entities/ultra_sniffer_ultra.png"),
     "Lord Pumpkinhead": ("born_in_chaos_v1/geo/lordofpumpkins.geo.json", "born_in_chaos_v1/textures/entities/lordofpumpkins.png"),
     "Tongbi, the Sculptor": ("mowziesmobs/geo/sculptor.geo.json", "mowziesmobs/textures/entity/sculptor.png")}  # was a PICK in renders.py
Z = {}
for j in sorted(glob.glob(JD + "/*.jar")):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for n in z.namelist():
        if n.startswith("assets/"): Z.setdefault(n, (j, z))
stem = lambda n: n.split("/")[-1].split(".")[0]
def anim_file(z, g):
    ns, rel = g.split("/")[1], g.split("/", 2)[2]
    named = sorted({"assets/%s/%s" % (ns, a.decode()) for n in z.namelist() if n.endswith(".class") and rel.encode() in (b := z.read(n))
                    for a in re.findall(rb"animations/[\w/.-]+\.json", b)} & set(Z))  # what the GeoModel naming this geometry loads
    same = [n for n in named if stem(n) == stem(g)] or [n for n in Z if n.startswith("assets/%s/" % ns) and "/animations/" in n and n.endswith(".json") and stem(n) == stem(g)]
    return (same or (named if len(named) == 1 else []) or [None])[0]
out = {}
for k, (g, t) in G.items():
    if ONLY and k not in ONLY: continue
    g, t = "assets/" + g, "assets/" + t
    if g not in Z or t not in Z: print("MISS", k, g in Z, t in Z); continue
    (j, z), tz = Z[g], Z[t][1]
    geo = json.loads(z.read(g)); png = tz.read(t); im = Image.open(io.BytesIO(png)).convert("RGBA")
    d = (geo.get("minecraft:geometry") or [{}])[0].get("description", {})
    af = anim_file(z, g); anims = json.loads(Z[af][1].read(af)).get("animations", {}) if af else {}
    idle = sorted((n for n in anims if "idle" in n.lower() and (stem(af) == stem(g) or stem(g) in n)), key=lambda n: (not re.search(r"idle$", n.lower()), len(n)))  # a shared file: only this mob's idle
    semi = sum(im.getchannel(3).histogram()[1:255])
    out[k] = {"key": k, "geo": geo, "texture": base64.b64encode(png).decode(), "texW": d.get("texture_width") or im.width,
              "texH": d.get("texture_height") or im.height, "alpha": "blend" if semi else "cutout", "glow": None,
              "anim": {"idle": anims[idle[0]]} if idle else {}, "animName": idle[0] if idle else None,
              "source": {"jar": j.split("/")[-1], "entries": [g, t] + ([af] if af else [])}}
    print(k, "|", j.split("/")[-1], "|", af and af.split("/")[-1], "|", idle[:1] or "rest pose", "|", "blend %d px" % semi if semi else "cutout")
json.dump(out, open(W + "/sb_geo_in.json", "w"))
print(len(out), "GeckoLib side bosses")
