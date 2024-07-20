'''Python Markdown FrontMatter Extension.

	This is a simple extension to python-markdown which enables one to 
	use a jekyll-like FrontMatter to store a yaml document object at the
	head of any markdown document.
'''
import re
import markdown, yaml

from markdown import Markdown

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension


class FrontMatterParser(Preprocessor):
	'''
	'''
	
	def __init__(self, md:markdown.core.Markdown, **kwargs):
		super().__init__(**kwargs)
		self.md = md
		if self.md:
			setattr(self.md, 'frontmatter', {})
		
		
	
	def run(self, lines:list[str]) -> list[str]:
		'''If frontmatter is present, extract it and store it in 
			self.md.frontmatter attribute.
		'''
		if lines[0] in ('---\n', '---'):
			numlines=len(lines)
			ender = -1
			for i in range(1, numlines):
				if lines[i] in ('---\n', '---'):
					ender = i
			if ender>0:
				FMtext = '\n'.join(lines[1:ender])
				lines=lines[ender+1:]
				self.md.frontmatter = yaml.load(FMtext, yaml.Loader)
		return lines
	
	def reset(self):
		'''Clear the frontmatter object for the next document.
		'''
		self.md.frontmatter={}
		super().reset()
	
class FrontMatterExtension(Extension):
	'''Extension object with hook for inclusion with Markdown.
	'''
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
	def extendMarkdown(self, md):
		md.registerExtension(self)
		md.preprocessors.register(
			FrontMatterParser(md), 'frontmatter_parser', 1024)
			
	


def makeExtension(**kwargs):
	'''Extension Factory Function
	'''
	return FrontMatterExtension(**kwargs)

	
