// Runs the pack's KubeJS server scripts against a stand-in for the recipe event and prints what they do to crafting
// recipes as JSON: {removed:[{id}|{output}…], added:[{type,output,count,pattern,key,ingredients}…]}. Only crafting
// (shaped/shapeless) is recorded; every other call is accepted and ignored, so the scripts run to the end.
// Usage: node kubejs_recipes.js <overrides/kubejs dir>  >  out.json
const fs = require("fs"), path = require("path"), vm = require("vm");
const root = process.argv[2], out = { removed: [], added: [] };
const any = () => new Proxy(function () {}, { get: (t, k) => k === Symbol.toPrimitive ? () => "" : any(), apply: () => any() });
const ingr = x => { if (x == null) return null; if (typeof x === "string") { const m = x.match(/^(\d+)x\s+(.*)$/); return m ? m[2] : x; } if (x.__item) return x.__item; if (x.item) return x.item; if (x.tag) return "#" + x.tag; return null; };
const stack = x => { if (typeof x === "string") { const m = x.match(/^(\d+)x\s+(.*)$/); return m ? [m[2], +m[1]] : [x, 1]; } if (x && x.__item) return [x.__item, x.__count || 1]; return [String(x), 1]; };
const Item = { of: (id, n) => { const [i, c] = stack(id); const o = { __item: i, __count: typeof n === "number" ? n : c }; return new Proxy(o, { get: (t, k) => k in t ? t[k] : () => p }); } }; const p = null;
const Ingredient = { of: x => ({ __item: ingr(x) }) };
const recipeEvent = (e = {}) => {
  const rec = (type, o) => { out.added.push(o.type ? o : Object.assign({ type }, o)); return any(); };
  return new Proxy({
    remove: f => { out.removed.push(f); },
    shaped: (o, pat, key) => { const [i, c] = stack(o); const k = {}; for (const [a, b] of Object.entries(key || {})) k[a] = ingr(b); return rec("shaped", { output: i, count: c, pattern: pat, key: k }); },
    shapeless: (o, ing) => { const [i, c] = stack(o); return rec("shapeless", { output: i, count: c, ingredients: [].concat(ing || []).flatMap(x => { const [a, n] = typeof x === "string" ? stack(x) : [ingr(x), 1]; return Array(n).fill(a); }) }); },
    custom: j => { if (j && /crafting_shaped|crafting_shapeless/.test(j.type || "")) { const r = j.result || {}; out.added.push({ type: /shaped/.test(j.type) ? "shaped" : "shapeless", output: r.item || r, count: r.count || 1, pattern: j.pattern, key: j.key && Object.fromEntries(Object.entries(j.key).map(([a, b]) => [a, ingr(Array.isArray(b) ? b[0] : b)])), ingredients: j.ingredients && j.ingredients.map(b => ingr(Array.isArray(b) ? b[0] : b)) }); } return any(); },
  }, { get: (t, k) => k in t ? t[k] : any() });
};
const ServerEvents = new Proxy({ recipes: fn => { try { fn(recipeEvent()); } catch (err) { process.stderr.write("script error: " + err.message + "\n"); } } }, { get: (t, k) => k in t ? t[k] : () => {} });
const ctx = vm.createContext({ ServerEvents, Item, Ingredient, console: { log() {}, info() {}, warn() {}, error() {} }, ItemEvents: any(), PlayerEvents: any(), EntityEvents: any(), BlockEvents: any(), LevelEvents: any(), Utils: any(), Fluid: any(), JsonIO: any(), Java: any(), global: {}, Platform: any(), Text: any(), Component: any() });
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(f => f.isDirectory() ? walk(path.join(d, f.name)) : f.name.endsWith(".js") ? [path.join(d, f.name)] : []);
for (const f of walk(path.join(root, "server_scripts")).sort()) {
  try { vm.runInContext(fs.readFileSync(f, "utf8"), ctx, { filename: f }); } catch (err) { process.stderr.write(path.relative(root, f) + ": " + err.message + "\n"); }
}
process.stdout.write(JSON.stringify(out));
