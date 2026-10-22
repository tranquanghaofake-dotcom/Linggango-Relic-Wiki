import json
def load():
    s=open('/home/user/Linggango-Relic-Wiki/build/src/gear_data.js').read()
    dec=json.JSONDecoder()
    GE,i=dec.raw_decode(s,9)
    GS,j=dec.raw_decode(s,i+4)
    k=s.index('Object.assign(IC,')+len('Object.assign(IC,')
    IC,_=dec.raw_decode(s,k)
    return GE,GS,IC,s
