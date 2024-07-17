from markdown import Extension

from cbr_website_beta.cbr__fastapi__markdown.markdown.md__pre_processors.Pre_Processor__IFrame import \
    Pre_Processor__IFrame
from cbr_website_beta.cbr__fastapi__markdown.markdown.md__pre_processors.Pre_Processor__QUnit import \
    Pre_Processor__QUnit


class Extension__QUnit(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(Pre_Processor__QUnit(md), 'qunit', 175)