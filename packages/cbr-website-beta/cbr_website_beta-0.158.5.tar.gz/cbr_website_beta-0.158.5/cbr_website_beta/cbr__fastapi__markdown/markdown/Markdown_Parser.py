from cbr_website_beta.cbr__fastapi__markdown.markdown.md__extensions.Extension__Chat_Bot import Extension__Chat_Bot
from cbr_website_beta.cbr__fastapi__markdown.markdown.md__extensions.Extension__IFrame import Extension__IFrame
from cbr_website_beta.cbr__fastapi__markdown.markdown.md__extensions.Extension__Mermaid         import Extension__Mermaid
from cbr_website_beta.cbr__fastapi__markdown.markdown.md__extensions.Extension__QUnit import Extension__QUnit
from cbr_website_beta.cbr__fastapi__markdown.markdown.md__extensions.Extension__Render_Template import Extension__Render_Template
from cbr_website_beta.cbr__fastapi__markdown.markdown.md__extensions.Extension__Video           import Extension__Video

from markdown                                           import Markdown
from osbot_utils.base_classes.Type_Safe                 import Type_Safe
from osbot_utils.context_managers.capture_duration import capture_duration
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.utils.Json import to_json_str


class Markdown_Parser(Type_Safe):


    def markdown(self):
        return Markdown(extensions=self.extensions())

    @cache_on_self
    def extensions(self):
        from markdown.extensions.attr_list  import AttrListExtension
        from markdown.extensions.def_list   import DefListExtension
        from markdown.extensions.footnotes  import FootnoteExtension
        from markdown.extensions.md_in_html import MarkdownInHtmlExtension
        from markdown.extensions.meta       import MetaExtension
        from markdown.extensions.tables     import TableExtension

        markdown_default_extensions = [ AttrListExtension           (),
                                        DefListExtension            (),
                                        FootnoteExtension           (),
                                        MarkdownInHtmlExtension     (),
                                        MetaExtension               (),
                                        TableExtension              ()]

        custom_extensions           = [ Extension__Chat_Bot         (),
                                        Extension__IFrame           (),
                                        Extension__Mermaid          (),
                                        Extension__QUnit            (),
                                        Extension__Render_Template  (),
                                        Extension__Video            ()]
        return markdown_default_extensions + custom_extensions

    def markdown_to_html(self, markdown_text):
        return self.parse(markdown_text).get('html')                # todo : refactor out the use of this method

    def content_to_html(self, content):
        return self.parse(content).get('html')

    def parse(self, markdown_text):
        markdown = self.markdown()
        html = markdown.convert(markdown_text)
        meta = markdown.Meta                        # this is from the MetaExtension
        from osbot_utils.utils.Dev import pprint
        return dict(markdown_text=markdown_text, html=html, meta=meta)


markdown_parser = Markdown_Parser()