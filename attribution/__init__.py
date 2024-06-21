import jinja2
from pydantic_yaml import parse_yaml_file_as
from attribution.model import Attributions, Attribution
import os

_module_dir = os.path.dirname(os.path.realpath(__file__))

value = parse_yaml_file_as(Attributions, os.path.join(_module_dir, "attributions.yaml"))

_template = jinja2.Template("""<ul>
{% for key, value in attributions.items() %}
<li>{{ value.html }}</li>
{% endfor %}
</ul>""", lstrip_blocks=True, trim_blocks=True)

html = _template.render(attributions=value.root)
