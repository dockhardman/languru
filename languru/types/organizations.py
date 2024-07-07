from enum import Enum
from types import MappingProxyType
from typing import Text, Union

from languru.exceptions import OrganizationNotFound

ALIASES_OPENAI = ("openai", "oai", "chatgpt")
ALIASES_AZURE = ("azure", "az", "azure_openai", "azoai", "aoai")
ALIASES_ANTHROPIC = ("anthropic", "ant", "claude")
ALIASES_GOOGLE = ("google", "goog", "gg")
ALIASES_GROQ = ("groq", "gq")
ALIASES_PERPLEXITY = ("perplexity", "pp", "perp", "pplx")
ALIASES_VOYAGE = ("voyage", "voy", "vg")


def to_org_type(org: Union[Text, "OrganizationType"]) -> "OrganizationType":
    if isinstance(org, OrganizationType):
        return org
    _org = org.casefold().strip().replace("-", "").replace("_", "")
    if _org in ALIASES_OPENAI:
        return OrganizationType.OPENAI
    if _org in ALIASES_AZURE:
        return OrganizationType.AZURE
    if _org in ALIASES_ANTHROPIC:
        return OrganizationType.ANTHROPIC
    if _org in ALIASES_GOOGLE:
        return OrganizationType.GOOGLE
    if _org in ALIASES_GROQ:
        return OrganizationType.GROQ
    if _org in ALIASES_PERPLEXITY:
        return OrganizationType.PERPLEXITY
    if _org in ALIASES_VOYAGE:
        return OrganizationType.VOYAGE
    raise OrganizationNotFound(f"Unknown organization: '{org}'.")


class OrganizationType(str, Enum):
    OPENAI = "openai"
    AZURE = "azure"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    PERPLEXITY = "perplexity"
    VOYAGE = "voyage"


organization_type_aliases = MappingProxyType(
    {
        OrganizationType.OPENAI: ALIASES_OPENAI,
        OrganizationType.AZURE: ALIASES_AZURE,
        OrganizationType.ANTHROPIC: ALIASES_ANTHROPIC,
        OrganizationType.GOOGLE: ALIASES_GOOGLE,
        OrganizationType.GROQ: ALIASES_GROQ,
        OrganizationType.PERPLEXITY: ALIASES_PERPLEXITY,
        OrganizationType.VOYAGE: ALIASES_VOYAGE,
    }
)
