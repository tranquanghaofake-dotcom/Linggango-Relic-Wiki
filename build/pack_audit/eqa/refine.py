import json,re,collections,sys
W=sys.argv[1]; m=json.load(open(W+'/equip_missing.json'))
ARM=r'_(helmet|chestplate|leggings|boots|hood|robe|robes|cap|tunic|pants|crown|mask|greaves|sabatons|helm|cuirass)$'
WEP=r'(sword|axe|bow|trident|spear|dagger|katana|scythe|halberd|glaive|rapier|cutlass|saber|sabre|claymore|mace|hammer|lance|staff|wand|blade|sickle|club|whip|gun|rifle|pistol|cannon|blaster|shotgun|tome|scepter|cleaver|knife|greatsword|moon|edge|fang|reaper)'
NOT=re.compile(r'(constructionwand|hole_filler|telescope|itemfilters|throwable|_flesh|mcwwindows|bbb:|wrench|_focus$|charged_staff|infinity_hammer|_template|smithing)')
out=[];drop=collections.Counter()
for x in m:
    i=x['id'];p=i.split(':')[1];ev=x['evidence']
    cls=[e for e in ev if e.startswith(('class:','attributesetter'))];tg=[e for e in ev if e.startswith('tag:')];nm='name' in ev
    if NOT.search(i): drop['blacklist']+=1;continue
    if cls and not tg and not nm:
        if x['kind']=='armor' and not re.search(ARM,p) and 'jet_suit' not in p: drop['material-class']+=1;continue
        if '/tiered' in cls[0] and 'attributesetter' not in ' '.join(ev) and not re.search(WEP,p): drop['tiered-nonweapon']+=1;continue
    if tg and not cls and not nm and all(t.startswith('tag:immersive_aircraft') for t in tg): drop['modtag']+=1;continue
    x['confidence']='high' if (cls or (tg and nm)) else ('tag-only' if tg else 'name-only')
    out.append(x)
json.dump(out,open(W+'/equip_missing.json','w'),indent=1)
print(len(out),drop,collections.Counter(x['confidence'] for x in out),collections.Counter(x['kind'] for x in out))
print(collections.Counter(x['mod'] for x in out).most_common(25)); print(sum(x['hidden_in_jei'] for x in out))
