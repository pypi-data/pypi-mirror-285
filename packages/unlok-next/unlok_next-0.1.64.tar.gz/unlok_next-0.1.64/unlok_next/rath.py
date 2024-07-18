import contextvars

from pydantic import Field
from rath import rath
from rath.links.auth import AuthTokenLink
from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.shrink import ShrinkingLink
from rath.links.split import SplitLink

current_unlok_next_rath = contextvars.ContextVar("current_unlok_next_rath")


class UnlokLinkComposition(TypedComposedLink):
    shrinking: ShrinkingLink = Field(default_factory=ShrinkingLink)
    dicting: DictingLink = Field(default_factory=DictingLink)
    auth: AuthTokenLink
    split: SplitLink


class UnlokRath(rath.Rath):
    """Unlok Rath

    Args:
        rath (_type_): _description_
    """

    link: UnlokLinkComposition = Field(default_factory=UnlokLinkComposition)

    async def __aenter__(self):
        print("UnlokRath.__aenter__")
        await super().__aenter__()
        current_unlok_next_rath.set(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        current_unlok_next_rath.set(None)
