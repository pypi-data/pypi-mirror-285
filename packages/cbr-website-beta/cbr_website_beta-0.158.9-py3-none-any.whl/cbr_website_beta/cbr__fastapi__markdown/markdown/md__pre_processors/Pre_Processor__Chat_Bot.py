import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from osbot_utils.utils.Misc import random_id


class Pre_Processor__Chat_Bot(Preprocessor):
    CHATBOT_RE_START = re.compile(r'\{\{chatbot\s+')
    CHATBOT_RE_END = re.compile(r'\}\}')

    def run(self, lines):
        new_lines = []
        in_chatbot_block = False
        buffer = []

        for line in lines:
            if in_chatbot_block:
                buffer.append(line)
                if self.CHATBOT_RE_END.search(line):
                    in_chatbot_block = False
                    chatbot_block = ''.join(buffer)
                    new_lines.append(self.convert_to_html(chatbot_block))
                    buffer = []
            elif self.CHATBOT_RE_START.search(line):
                in_chatbot_block = True
                buffer.append(line)
            else:
                new_lines.append(line)
        return new_lines

    def convert_to_html(self, text):
        pattern = re.compile(
            r'\{\{chatbot\s+(.*?)\s*\}\}'
        )
        match = pattern.search(text.replace("\n", " "))
        if match:
            attrs_text = match.group(1)
            attr_pattern = re.compile(
                r'(\w+)\s*=\s*"([^"]*)"'
            )
            attrs = attr_pattern.findall(attrs_text)
            attr_dict = {key: value for key, value in attrs}

            if 'channel' not in attr_dict:
                attr_dict['channel'] = random_id()
            attr_str = ' '.join(
                f'{key}="{value}"' for key, value in attr_dict.items()
            )
            return f'<chatbot-openai {attr_str}></chatbot-openai>'
        return text


class Extension__Chat_Bot(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(Pre_Processor__Chat_Bot(md), 'chatbot', 175)
