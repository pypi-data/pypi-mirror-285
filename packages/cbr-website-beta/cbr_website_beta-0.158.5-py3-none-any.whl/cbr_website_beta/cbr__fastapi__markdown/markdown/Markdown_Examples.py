from osbot_utils.base_classes.Type_Safe import Type_Safe


class Markdown_Examples:

    def all_examples(self):

        return dict(
                    markdown_extra  = self.markdown_extra (),
                    markdown        = self.markdown       (),
                    mermaid         = self.mermaid        (),
                    extensions      = self.extensions     (),
                    render_template = self.render_template())


    def extensions(self):
        examples = {}
        def add_example(title, extension, args=''):
            examples[title] = f'{{{{{extension} {args } }}}}\n'

        args = """system_prompt="only speak in emojies"
                  name="Custom bot" 
                  platform  = "Groq (Free)"
                  provider  = "1. Meta" 
                  model     = "llama3-70b-8192" 
                  edit_mode = "false"
                  """
        add_example('chatbot', 'chatbot', args=args )
        return examples

    def markdown(self):
        hello_world = "hello world"
        headers     = '## Headers\n\n# Header 1\n## Header 2\n### Header 3\n#### Header 4\n##### Header 5\n###### Header 6\n\n'
        links       = '## Links\n\n - [The Cyber Boardroom](https://thecyberboardroom.com)\n- [Google](https://www.google.com)\n\n'
        formatting  = "## Formatting\n\n**bold**\n\n*italic*\n\n~~strikethrough~~\n\n`code`\n\n"
        lists       = "## Lists\n\n- item 1\n- item 2\n- item 3\n\n1. item 1\n2. item 2\n3. item 3\n\n"
        code_blocks = "## Code Blocks\n\n```python\nprint('hello world')\n```\n\n"
        images      = "## Images\n\n<img src='/assets/cbr/cbr-logo-community.png' width='300px'/>\n\n![image](/assets/cbr/cbr-logo-community.png)\n\n"
        quotes      = "## Quotes\n\n> quote 1\n\ntext\n\n> quote 2\n\n"

        items_to_show = ['hello_world', 'headers', 'links', 'formatting', 'lists',
                         'code_blocks', 'images','quotes']

        return {item: locals()[item] for item in items_to_show}

    def markdown_extra(self):
        examples = {}

        def add_example(title, markdown_text):
            examples[title] = markdown_text

        add_example('tables', "## Tables\n\n| Header 1 | Header 2 | Header 3 |\n|----------|----------|----------|\n| cell 1   | cell 2   | cell 3   |\n\n")
        add_example('attribute lists', '[link as button](http://example.com){: class="btn btn-primary" title="Some title!" }\n\n'
                                                          'This is a paragraph.\n{: #an_id .a_class }\n\n'
                                                          'A setext style header {: #setext}\n=================================\n### A hash style header ### {: #hash }\n\n'
                                                          '| set on td    | set on em   |\n|--------------|-------------|\n| *a* { .foo } | *b*{ .foo } |')
        add_example('definition lists', """Apple\n:   Pomaceous fruit of plants of the genus Malus in\n    the family Rosaceae.\n\nOrange\n:   The fruit of an evergreen tree of the genus Citrus.""")
        add_example('footnotes', """\nFootnotes[^1] have a label[^@#$%] and the footnote's content.\n\n[^1]: This is a footnote content.\n[^@#$%]: A footnote on the label: "@#$%".""")
        return examples
    def mermaid(self):

        examples = {}

        def add_example(title, mermaid_code):
            examples[title] = f'```mermaid\n{mermaid_code}\n```\n'

        add_example('simple Graph (TD)'         , 'graph TD;\n    A-->B;\n    A-->C;\n    B-->D;\n    C-->D;')
        add_example('simple Graph (RL)'         , 'graph RL;\n    A-->B;\n    A-->C;\n    B-->D;\n    C-->D;')
        add_example('pie - netflix'             , MERMAID__PIE__NETFLIX             )
        add_example('sequence diagram'          , MERMAID__Sequence_Diagram         )
        add_example('sequence diagram (complex)', MERMAID__Sequence_Diagram_Complex )
        add_example('flowchat with styles'      , MERMAID__Flowchart_with_styles    )
        add_example('git commit flow'           , MERMAID__Git_Commit_Flow          )
        add_example('mind map'                  , MERMAID__MindMap                  )
        return examples

    def render_template(self):
        examples = {}

        def add_example(title, path_to_template):
            markdown_example = f'## {title} \n\n this is the server side rendering of this template\n\n{{{{render_template("{path_to_template}")}}}}'
            examples[title] = markdown_example

        add_example('includes/login_required.html', 'includes/login_required.html')

        # for now remove these since they are not being removed on reload (and if the user start typing on the preview, we will get tons of new version))
        #add_example('llms/chat_with_llms/single.html (only speak in emojis)', 'llms/chat_with_llms/single.html')
        #add_example('llms/chat_with_llms/three-languages.html', 'llms/chat_with_llms/six-languages.html')

        add_example('terms and conditions', 'home/terms_and_conditions.html')
        add_example('content - incident management', 'home/content/incident-management.html')
        return examples

RENDER_TEMPLATE = """'''
This is a Markdown content.

    
'''"""

MERMAID__PIE__NETFLIX= """\
pie title NETFLIX
    "Time spent looking for movie" : 90
    "Time spent watching it" : 10"""

MERMAID__Sequence_Diagram = """\
sequenceDiagram
    Alice ->> Bob: Hello Bob, how are you?
    Bob-->>John: How about you John?
    Bob--x Alice: I am good thanks!
    Bob-x John: I am good thanks!
    Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.
    Bob-->Alice: Checking with John...
    Alice->John: Yes... John, how are you?"""

MERMAID__Flowchart_with_styles= """\
graph TB
    sq[Square shape] --> ci((Circle shape))
    subgraph A
        od>Odd shape]-- Two line<br/>edge comment --> ro
        di{Diamond with <br/> line break} -.-> ro(Rounded<br>square<br>shape)
        di==>ro2(Rounded square shape)
    end
    %% Notice that no text in shape are added here instead that is appended further down
    e --> od3>Really long text with linebreak<br>in an Odd shape]
    %% Comments after double percent signs
    e((Inner / circle<br>and some odd <br>special characters)) --> f(,.?!+-*ز)
    cyr[Cyrillic]-->cyr2((Circle shape Начало));
     classDef green fill:#9f6,stroke:#333,stroke-width:2px;
     classDef orange fill:#f96,stroke:#333,stroke-width:4px;
     class sq,e green
     class di orange"""

MERMAID__Sequence_Diagram_Complex = """\
sequenceDiagram
    participant web as Web Browser
    participant blog as Blog Service
    participant account as Account Service
    participant mail as Mail Service
    participant db as Storage
    Note over web,db: The user must be logged in to submit blog posts
    web->>+account: Logs in using credentials
    account->>db: Query stored accounts
    db->>account: Respond with query result
    alt Credentials not found
        account->>web: Invalid credentials
    else Credentials found
        account->>-web: Successfully logged in
        Note over web,db: When the user is authenticated, they can now submit new posts
        web->>+blog: Submit new post
        blog->>db: Store post data
        par Notifications
            blog--)mail: Send mail to blog subscribers
            blog--)db: Store in-site notifications
        and Response
            blog-->>-web: Successfully posted
        end
    end"""


MERMAID__Git_Commit_Flow = """\
gitGraph:
    commit "Ashish"
    branch newbranch
    checkout newbranch
    commit id:"1111"
    commit tag:"test"
    checkout main
    commit type: HIGHLIGHT
    commit
    merge newbranch
    commit
    branch b2
    commit"""

MERMAID__MindMap = """\
mindmap
  root((Problem))
    Category A
      Cause A
        Cause C
    Category B
      Cause B
        Cause D
        Cause E
    Category C
      Usual Cause A
      Usual Cause B
    Category D
      Usual Cause C
      Usual Cause D"""




markdown_examples = Markdown_Examples()