import re

from markdown.preprocessors import Preprocessor


class Pre_Processor__QUnit(Preprocessor):

    QUNIT_RE = re.compile(r'\{\{qunit:(.+?)\}\}')
    # <link   href="/assets/qunit/lib/qunit-2.21.0.css" rel="stylesheet" >
    # <link   href="https://krinkle.github.io/qunit-theme-ninja/qunit.css" rel="stylesheet" >
    # <link   href="https://krinkle.github.io/qunit-theme-gabe/qunit-theme-gabe.css" rel="stylesheet" >
    # <link   href="https://bryce.io/qunit-theme-burce/qunit-theme-burce.css" rel="stylesheet" >
    def run(self, lines):
        new_lines = []
        for line in lines:
            match = self.QUNIT_RE.search(line)
            if match:
                path = match.group(1).strip()
                qunit_html = f"""\
                
<link   href="/assets/qunit/lib/qunit-theme-gabe.css" rel="stylesheet" >

    
<style>    

#qunit-testrunner-toolbar {{
    display: none;
}}
#qunit-header {{
    display: none;
}}
#qunit-userAgent {{
    display: none;
}}

</style>

<script src ="/assets/plugins/jquery/dist/jquery.min.js"           ></script>
<script src ="/assets/qunit/lib/qunit-2.21.0.js"                   ></script>
             
<div id="qunit-container">
    <div id="qunit"></div>
    <div id="qunit-fixture"></div>
</div>
<script type="module" src="/web_components/qunit/{path}"></script>
"""

                new_lines.append(qunit_html)
            else:
                new_lines.append(line)
        return new_lines