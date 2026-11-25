import re
s=open("report.md",encoding="utf-8").read().replace("\r\n","\n")

# 1. title block -> YAML metadata
i=s.index("| | |")
s=s[i:]
yaml=('---\n'
 'title: "Cryptographic Transparency in the Supply Chain"\n'
 'subtitle: "A CBOM profile approach to post-quantum migration readiness"\n'
 'author: "PKI Consortium CBOM Profiles Working Group"\n'
 'date: "September 2026"\n'
 'lang: en-GB\n'
 '---\n\n')

# 2. details table: single version row, drop the standalone date row
s=re.sub(r'\| \*\*Version\*\* \|[^|]*\|', '| **Version** | v0.9 — draft for Commission review |', s, count=1)
s=re.sub(r'\n\| \*\*Date\*\* \|[^|]*\|', '', s, count=1)

# 3. drop the markdown contents; Word gets a real TOC field
a=s.index("\n---\n\n## Contents")
b=s.index("\n## How to read this report")
s=s[:a]+"\n\\newpage\n"+s[b:]

# 4. size the figures to the text column
s=re.sub(r'(!\[[^\]]*\]\(figures/[^)]+\))', r'\1{width=16cm}', s)

open("report.pandoc.md","w",encoding="utf-8").write(yaml+s)
print("pandoc source rebuilt", s.count("{width=16cm}"), "figures")
