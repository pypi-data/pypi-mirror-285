from beanie import Document, Indexed

from fa_common.models import TimeStampedModel

from .types import Module


class ModuleDocument(Module, Document, TimeStampedModel):
    sku: Indexed(str, unique=True)
