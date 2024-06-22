from pydantic import BaseModel, RootModel, computed_field
from typing import Dict, Optional
import jinja2

_template = jinja2.Template("""<div>
<p><a href="{{ url }}">{{ name }}</a></p>
<p>License:&nbsp;
{%- for license in licenses %}
{%- if loop.length > 1 %}{%- if loop.last %},&nbsp;or&nbsp;{%- elif not loop.first %},&nbsp;{%- endif %}{%- endif %}
<a href="{{ license.url }}">{{ license.name }}</a>
{%- endfor %}</p>
<div>{{ description | safe }}</div>
</div>""", lstrip_blocks=True, trim_blocks=True)


class LicenseInfo(BaseModel):
    name: str
    url: Optional[str] = None


class Attribution(BaseModel):
    name: str
    url: Optional[str] = None
    licenses: list[LicenseInfo]
    description: str

    @computed_field
    @property
    def html(self) -> str:
        return _template.render(
            name=self.name,
            url=self.url,
            description=self.description,
            licenses=self.licenses,
        )


class Attributions(RootModel):
    root: Dict[str, Attribution]
