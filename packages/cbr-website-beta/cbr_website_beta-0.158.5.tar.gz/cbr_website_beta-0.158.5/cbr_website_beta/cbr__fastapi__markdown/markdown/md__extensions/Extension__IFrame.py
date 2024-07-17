from markdown import Extension

from cbr_website_beta.cbr__fastapi__markdown.markdown.md__pre_processors.Pre_Processor__IFrame import \
    Pre_Processor__IFrame


class Extension__IFrame(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(Pre_Processor__IFrame(md), 'iframe', 175)