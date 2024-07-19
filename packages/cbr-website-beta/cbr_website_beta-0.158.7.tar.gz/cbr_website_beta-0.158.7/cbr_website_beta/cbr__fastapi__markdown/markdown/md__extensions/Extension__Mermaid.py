
from markdown import Extension

from cbr_website_beta.cbr__fastapi__markdown.markdown.md__block_processors.Block_Processor__Mermaid import \
    Block_Processor__Mermaid


class Extension__Mermaid(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(Block_Processor__Mermaid(md.parser), 'mermaid', 175)

    def __repr__(self):
        return f'Markdown__Ex__Mermaid'



