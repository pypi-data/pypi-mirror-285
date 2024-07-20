from markdown import Markdown


md = Markdown(extensions=['pymd_frontmatter'])
hr = '='*64

with open('test.md', 'r') as f:
	txt = f.read()

html = md.convert(txt)
print(md.frontmatter or "Not available")
print(hr)
print(html)
print(hr, '\n', hr)

md = Markdown(extensions=['frontmatter'])
with open('test2.md', 'r') as f:
	txt = f.read()

html = md.convert(txt)
print(md.frontmatter)
print(hr)
print (html)
