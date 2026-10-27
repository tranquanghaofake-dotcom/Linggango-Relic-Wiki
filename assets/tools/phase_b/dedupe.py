"""Mark exact duplicates in the catalog (same sha256): the first row of the highest tier keeps the file, the others get duplicate_of.
Usage: python3 -I dedupe.py <assets>"""
import csv,sys,os
A=sys.argv[1]; p=os.path.join(A,'catalog.csv'); R=list(csv.DictReader(open(p))); K=list(R[0].keys())
order={'A':0,'A-perm':1,'A-SA':2}; first={}
for r in sorted(R,key=lambda r:(order.get(r['tier'],9),r['id'])):
    h=r['sha256']
    if h in first and first[h]!=r['id']: r['duplicate_of']=first[h]
    else: first.setdefault(h,r['id'])
with open(p,'w',newline='') as f: w=csv.DictWriter(f,fieldnames=K); w.writeheader(); w.writerows(R)
print(len(R),'rows,',sum(1 for r in R if r['duplicate_of']),'exact duplicates')
