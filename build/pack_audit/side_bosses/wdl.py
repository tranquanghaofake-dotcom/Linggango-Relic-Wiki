import json,subprocess,sys,urllib.parse,os
W=sys.argv[1]
P={"Frostmaw":("mowziesmobs.fandom.com","260px-Entity MOWM Frostmaw.png"),"Naga":("mowziesmobs.fandom.com","Naga New.webp"),"Ferrous Wroughtnaut":("mowziesmobs.fandom.com","Ferrous Wroughtnaut.png"),
"Netherite Monstrosity":("lendercataclysm.wiki.gg","Netherite Monstrosity.png"),"Ender Guardian":("lendercataclysm.wiki.gg","Ender Guardian.png"),"Ancient Remnant":("lendercataclysm.wiki.gg","Ancient Remnant.png"),"Ignis":("lendercataclysm.wiki.gg","Ignis.png"),"The Harbinger":("lendercataclysm.wiki.gg","The Harbinger.png"),"The Leviathan":("lendercataclysm.wiki.gg","The Leviathan.png"),"Maledictus":("lendercataclysm.wiki.gg","Maledictus.png"),"Scylla":("lendercataclysm.wiki.gg","Scylla.png"),
"Luxtructosaurus":("alexscaves.wiki.gg","Luxtructosaurus.webp"),"Forsaken":("alexscaves.wiki.gg","Forsaken.webp"),"Vizier":("goety.wiki.gg","Vizier.png"),"Apostle":("goety.wiki.gg","Apostle.png"),"Redstone Monstrosity":("goety.wiki.gg","RM Standing.gif"),"Forgotten Guardian":("the-undergarden-mod.fandom.com","Forgotten Guardian.png")}
U={}
for b,(h,f) in P.items():
  q=urllib.parse.quote('File:'+f)
  d=json.loads(subprocess.run(['curl','-sS','-m','25',f'https://{h}/api.php?action=query&prop=imageinfo&iiprop=url&titles={q}&format=json'],capture_output=True,text=True).stdout or '{}')
  pg=list(d.get('query',{}).get('pages',{}).values())
  try:url=pg[0]['imageinfo'][0]['url']
  except Exception:print('nourl',b);continue
  out=W+'/wimg/'+b.replace(' ','_')+os.path.splitext(f)[1]
  subprocess.run(['curl','-sS','-L','-m','40','-o',out,url]);U[b]={'url':url,'file':out,'page':f'https://{h}/wiki/'+urllib.parse.quote('File:'+f.replace(' ','_'))}
  print(b,url,os.path.getsize(out))
json.dump(U,open(W+'/wimg/dl.json','w'),indent=0)
