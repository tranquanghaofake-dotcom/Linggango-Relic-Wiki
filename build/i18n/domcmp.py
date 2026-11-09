"""Compares two build/i18n/domdump.js outputs: prints every route state whose title, <main>, sidebar or title-screen buttons differ, with the first difference. Usage: domcmp.py before.json after.json"""
import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); bad=0
for k in a:
    for f in ('title','main','side','tbtns'):
        if a[k][f]!=b[k][f]:
            bad+=1; x,y=a[k][f],b[k][f]; i=next((i for i in range(min(len(x),len(y))) if x[i]!=y[i]),min(len(x),len(y)))
            print('DIFF',k,f,'at',i,'\n   base:',repr(x[max(0,i-60):i+80]),'\n   new :',repr(y[max(0,i-60):i+80]))
print(len(a),'routes compared;',bad,'differences')
