try:from getch import getch
except ModuleNotFoundError:
 def getch():raise ModuleNotFoundError('need getch module install with: "pip install multi-getch"')
def bf_exec(source,input=lambda:ord(getch()),output=lambda b:print(end=chr(b),flush=1)):
 a,b,c,d,e,f=''.join(b for b in str(source) if b in '<>+-,.[]'),{},[],[0],0,0
 for g,h in enumerate(a):
  if h=='[':c.append(g)
  if h==']':
   if not c:raise SyntaxError("unbalanced brackets")
   i=c.pop();b[i]=g;b[g]=i
 if c:raise SyntaxError("unbalanced brackets")
 while e<len(a):
  j=a[e]
  if j=='>':
   f+=1
   if f==len(d):d.append(0)
  elif j=='<':f=max(f-1,0)
  elif j=='+':d[f]=(d[f]+1)%256
  elif j=='-':d[f]=(d[f]-1)%256
  elif j==',':d[f]=int(input())%256
  elif j=='.':output(d[f])
  elif j=='[' and d[f]==0:e=b[e]
  elif j==']' and d[f]!=0:e=b[e]
  e+=1