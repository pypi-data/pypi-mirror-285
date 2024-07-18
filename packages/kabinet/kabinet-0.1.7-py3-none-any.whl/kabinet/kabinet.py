from koil.composition import Composition
from pydantic import Field

from kabinet.rath import KabinetRath


class Kabinet(Composition):
    rath: KabinetRath = Field(default_factory=KabinetRath)

    def _repr_html_inline_(self):
        return f"""<p>Kabinet </p>"""
