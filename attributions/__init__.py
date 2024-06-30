import os

import markdown

_module_dir = os.path.dirname(os.path.realpath(__file__))
_src: str
with open(os.path.join(_module_dir, "attribution.md")) as f:
    _src = f.read()

html = markdown.markdown(_src)
