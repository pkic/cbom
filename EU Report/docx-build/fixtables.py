import re
P="word/document.xml"
s=open(P,encoding="utf-8").read()
TW=9072          # A4 text width in twips
MAR=216          # left+right cell margin
STRIP="()[],.;:·—–·’'\"/"

def runs(c):
    """(text, is_code) per run"""
    out=[]
    for r in re.findall(r'<w:r>.*?</w:r>',c,re.S):
        t="".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>',r))
        if t: out.append((t,'VerbatimChar' in r))
    return out

def widths(tbl):
    grid=len(re.findall(r'<w:gridCol[ /]',tbl))
    if not grid: return None
    mass=[1.0]*grid; need=[300.0]*grid
    for r in re.findall(r'<w:tr[ >].*?</w:tr>',tbl,re.S):
        cs=re.findall(r'<w:tc>.*?</w:tc>',r,re.S)
        for j,c in enumerate(cs[:grid]):
            tot=0.0; longest=0.0
            for t,code in runs(c):
                cw=114.0 if code else 101.0
                tot+=len(t)*cw
                for w in t.split():
                    longest=max(longest,len(w.strip(STRIP))*cw)
            mass[j]=max(mass[j],tot)
            need[j]=max(need[j],longest+MAR)
    wt=[m**0.6 for m in mass]
    # a column whose longest cell is essentially one token must not wrap
    hard=[j for j in range(grid)
          if need[j]>=0.70*mass[j] and need[j]<=TW*0.25]
    soft=[j for j in range(grid) if j not in hard]
    out=[0.0]*grid
    res=sum(need[j] for j in hard)
    if not soft:
        tot=sum(wt); out=[TW*wt[j]/tot for j in range(grid)]
        for j in range(grid): out[j]=max(out[j],need[j])
    else:
        if res>TW*0.55:
            k=TW*0.55/res; res=TW*0.55
        else: k=1.0
        for j in hard: out[j]=need[j]*k
        rest=TW-res; tot=sum(wt[j] for j in soft)
        for j in soft: out[j]=rest*wt[j]/tot
    # lift any remaining near-miss so short tokens stop breaking
    for _ in range(8):
        lo=[j for j in range(grid) if out[j]<need[j] and need[j]<=TW*0.22]
        if not lo: break
        j=min(lo,key=lambda j: need[j]-out[j])
        k=max(range(grid),key=lambda k: out[k])
        d=need[j]-out[j]
        if k==j or out[k]-d < TW*0.13: break
        out[j]+=d; out[k]-=d
    sc=TW/sum(out); out=[int(round(x*sc)) for x in out]
    out[-1]+=TW-sum(out)
    return out

def fix(m):
    t=m.group(0)
    w=widths(t)
    if not w: return t
    t=re.sub(r'<w:tblW [^/]*/>','<w:tblW w:w="%d" w:type="dxa"/>'%TW,t,count=1)
    t=t.replace('<w:tblLayout w:type="fixed"/>','')
    t=re.sub(r'(<w:tblLook )','<w:tblLayout w:type="fixed"/>\\1',t,count=1)
    it=iter(w)
    t=re.sub(r'<w:gridCol[^/]*/>',lambda _:'<w:gridCol w:w="%d"/>'%next(it),t)
    def row(rm):
        r=rm.group(0); ri=iter(w)
        def tc(cm):
            c=cm.group(0); cw='<w:tcW w:w="%d" w:type="dxa"/>'%next(ri,w[-1])
            if '<w:tcPr />' in c or '<w:tcPr/>' in c:
                return re.sub(r'<w:tcPr ?/>','<w:tcPr>'+cw+'</w:tcPr>',c,count=1)
            if re.search(r'<w:tcW [^/]*/>',c):
                return re.sub(r'<w:tcW [^/]*/>',cw,c,count=1)
            return re.sub(r'<w:tcPr>','<w:tcPr>'+cw,c,count=1)
        return re.sub(r'<w:tc>.*?</w:tc>',tc,r,flags=re.S)
    return re.sub(r'<w:tr[ >].*?</w:tr>',row,t,flags=re.S)

s=re.sub(r'<w:tbl>.*?</w:tbl>',fix,s,flags=re.S)
open(P,"w",encoding="utf-8").write(s)

# code in tables: 11pt Consolas is wider than the 9pt body around it
q="word/styles.xml"; x=open(q,encoding="utf-8").read()
x=x.replace('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" />\n      <w:sz w:val="22" />',
            '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" />\n      <w:sz w:val="17" /><w:szCs w:val="17" />')
open(q,"w",encoding="utf-8").write(x)
print("tables sized")
