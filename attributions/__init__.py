from typing import Sequence

import jinja2
from pydantic_yaml import parse_yaml_file_as
from attributions.model import Attributions, Attribution
import os

_module_dir = os.path.dirname(os.path.realpath(__file__))

value = parse_yaml_file_as(Attributions, os.path.join(_module_dir, "attributions.yaml"))

_template = jinja2.Template("""<ul>
{% for key, value in items %}
<li>{{ value.html }}</li>
{% endfor %}
</ul>""", lstrip_blocks=True, trim_blocks=True)

html = _template.render(items=sorted(value.root.items()))


def lookup(keys: list[str]) -> dict[str, Attribution]:
    return dict([(key, value.root[key]) for key in keys])
