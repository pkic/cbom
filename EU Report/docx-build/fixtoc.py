s=open("word/document.xml",encoding="utf-8").read()
i=s.find("How to read this report"); pstart=s.rfind("<w:p>",0,i)
toc=('<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Contents</w:t></w:r></w:p>'
 '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
 '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r>'
 '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
 '<w:r><w:rPr><w:i/><w:color w:val="6B6B6B"/></w:rPr>'
 '<w:t xml:space="preserve">Right-click and choose Update Field to build the table of contents.</w:t></w:r>'
 '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
open("word/document.xml","w",encoding="utf-8").write(s[:pstart]+toc+s[pstart:])
print("toc field in")
