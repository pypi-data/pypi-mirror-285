import re

from markdown.preprocessors import Preprocessor


class Pre_Processor__IFrame(Preprocessor):

    IFRAME_RE = re.compile(r'\{\{iframe:(.+?)\}\}')

    def run(self, lines):
        new_lines = []
        for line in lines:
            match = self.IFRAME_RE.search(line)
            if match:
                url = match.group(1).strip()
                iframe_html = f'<iframe src="{url}" width="100%" height="500px" style="border:1px solid"></iframe>'
                new_lines.append(iframe_html)
            else:
                new_lines.append(line)
        return new_lines