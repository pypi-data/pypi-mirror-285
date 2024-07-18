from pydantic import Field
from rath import rath
import contextvars

from rath.links.auth import AuthTokenLink

from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.shrink import ShrinkingLink
from rath.links.split import SplitLink

current_kabinet_rath = contextvars.ContextVar("current_kabinet_rath")


class KabinetLinkComposition(TypedComposedLink):
    shrinking: ShrinkingLink = Field(default_factory=ShrinkingLink)
    dicting: DictingLink = Field(default_factory=DictingLink)
    auth: AuthTokenLink
    split: SplitLink


class KabinetRath(rath.Rath):
    """Kabinet Rath

    Args:
        rath (_type_): _description_
    """

    link: KabinetLinkComposition = Field(default_factory=KabinetLinkComposition)

    async def __aenter__(self):
        await super().__aenter__()
        current_kabinet_rath.set(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)
        current_kabinet_rath.set(None)
