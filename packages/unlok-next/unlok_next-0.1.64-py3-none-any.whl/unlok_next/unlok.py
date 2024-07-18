from koil.composition import Composition
from pydantic import Field

from unlok_next.rath import UnlokRath


class Unlok(Composition):
    rath: UnlokRath = Field(default_factory=UnlokRath)

    def _repr_html_inline_(self):
        return f"""<p>Unlok </p>"""
