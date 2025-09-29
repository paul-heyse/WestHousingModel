from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass
class ModelError(Exception):
    message: str
    context: Optional[Mapping[str, Any]] = None

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} [context: {', '.join(f'{k}={v!r}' for k, v in self.context.items())}]"
        return self.message


class RegistryError(ModelError):
    pass


class SchemaError(ModelError):
    pass


class ConnectorError(ModelError):
    pass


class CacheError(ModelError):
    pass


class ComputationError(ModelError):
    pass


class ExportError(ModelError):
    pass


__all__ = [
    "ModelError",
    "RegistryError",
    "SchemaError",
    "ConnectorError",
    "CacheError",
    "ComputationError",
    "ExportError",
]
