import re
import xml.etree.ElementTree    as etree
from markdown.blockprocessors   import BlockProcessor

RE__BLOCK__MERMAID = re.compile(r'^\s*```mermaid\s*\n(.*?)\n\s*```\s*$', re.DOTALL | re.MULTILINE)

class Block_Processor__Mermaid(BlockProcessor):

    def test(self, parent, block):
        return bool(RE__BLOCK__MERMAID.search(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = RE__BLOCK__MERMAID.search(block)
        if m:
            code = m.group(1)
            pre = etree.SubElement(parent, 'pre')
            pre.set('class', 'mermaid')
            pre.text = code


# script = etree.SubElement(parent, 'script')
# script.set('type', 'module')
# script.text = """
#     import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs';
#     mermaid.initialize({ startOnLoad: true });
# """