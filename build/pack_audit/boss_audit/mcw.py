import urllib.request,urllib.parse,json,sys
def q(p):
  u='https://minecraft.wiki/api.php?'+urllib.parse.urlencode(dict(p,format='json'))
  return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30))
out={}
for page in sys.argv[2:]:
  d=q({'action':'query','titles':page,'prop':'pageimages','piprop':'original','redirects':1})
  for p in d['query']['pages'].values():
    out[page]=p.get('original',{}).get('source')
  print(page,out[page])
json.dump(out,open(sys.argv[1],'w'))
