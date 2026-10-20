import json,subprocess,sys,urllib.parse,re
W=sys.argv[1]
L={"Swampjaw":("ftb.fandom.com","Swampjaw"),"Bellringer":("ftb.fandom.com","Bellringer"),"Dame Fortuna":("ftb.fandom.com","Dame Fortuna"),"Rosalyne":("ftb.fandom.com","Rosalyne, Blade of Dusk"),
"Frostmaw":("mowziesmobs.fandom.com","Frostmaw"),"Naga":("mowziesmobs.fandom.com","Naga"),"Ferrous Wroughtnaut":("mowziesmobs.fandom.com","Ferrous Wroughtnaut"),
"Netherite Monstrosity":("lendercataclysm.wiki.gg","Netherite Monstrosity"),"Ender Guardian":("lendercataclysm.wiki.gg","Ender Guardian"),"Ancient Remnant":("lendercataclysm.wiki.gg","Ancient Remnant"),"Ignis":("lendercataclysm.wiki.gg","Ignis"),"The Harbinger":("lendercataclysm.wiki.gg","The Harbinger"),"The Leviathan":("lendercataclysm.wiki.gg","The Leviathan"),"Maledictus":("lendercataclysm.wiki.gg","Maledictus"),"Scylla":("lendercataclysm.wiki.gg","Scylla"),
"Luxtructosaurus":("alexscaves.wiki.gg","Luxtructosaurus"),"Forsaken":("alexscaves.wiki.gg","Forsaken"),
"Vizier":("goety.wiki.gg","Vizier"),"Apostle":("goety.wiki.gg","Apostle"),"Redstone Monstrosity":("goety.wiki.gg","Redstone Monstrosity"),
"Forgotten Guardian":("the-undergarden-mod.fandom.com","Forgotten Guardian"),"Lord Pumpkinhead":("borninchaosmod.fandom.com","Lord Pumpkinhead")}
def get(u):
  return json.loads(subprocess.run(['curl','-sS','-m','25',u],capture_output=True,text=True).stdout or '{}')
R={}
for b,(h,t) in L.items():
  q=urllib.parse.quote(t)
  d=get(f'https://{h}/api.php?action=query&prop=pageimages|images&titles={q}&pithumbsize=400&imlimit=50&format=json&redirects=1')
  pg=list(d.get('query',{}).get('pages',{}).values())
  if not pg:print(b,'nopage');continue
  pg=pg[0];cand=[]
  if 'thumbnail' in pg:cand.append(('thumb',pg['thumbnail']['source']))
  ims=[i['title'] for i in pg.get('images',[])]
  R[b]={'cand':cand,'images':ims,'host':h,'page':f'https://{h}/wiki/{q}'}
  print(b,cand,ims[:12])
json.dump(R,open(W+'/wimg/cand.json','w'),indent=0)
