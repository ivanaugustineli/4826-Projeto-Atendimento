from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AtenTipo(str, Enum):
    INC = "INC"
    PRB = "PRB"
    RITM = "RITM"
    SCTASK = "SCTASK"


class AtendimentoBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atenNumero: str | int = Field(description="ID interno")
    atenNumeroCliente: str = Field(default="", description="ID principal no cliente")
    atenNumeroSecundario: str = Field(
        default="", description="Tarefa ou atendimento original"
    )
    atenAssunto: str = Field(default="", description="Descricao resumida")
    atenDescricao: str = Field(default="", description="Texto completo")
    atenDataAbertura: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Abertura no cliente",
    )
    atenDataRecepcao: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Chegada para analise",
    )
    atenAnalistaCliente: str = Field(default="", description="Responsavel no cliente")
    atenAnalistaInterno: str = Field(default="", description="Responsavel interno")
    atenCausa: str = Field(default="", description="Causa raiz")
    atenSolucao: str = Field(default="", description="Resolucao")
    atenObservacao: str = Field(default="", description="Notas adicionais")
    atenTipo: AtenTipo


class AtendimentoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atenNumero: str | int | None = Field(
        default=None,
        description="ID interno; se omitido, sera gerado a partir do _id do MongoDB",
    )
    atenNumeroCliente: str = ""
    atenNumeroSecundario: str = ""
    atenAssunto: str = ""
    atenDescricao: str = ""
    atenDataAbertura: datetime | None = None
    atenDataRecepcao: datetime | None = None
    atenAnalistaCliente: str = ""
    atenAnalistaInterno: str = ""
    atenCausa: str = ""
    atenSolucao: str = ""
    atenObservacao: str = ""
    atenTipo: AtenTipo


class AtendimentoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atenNumero: str | int | None = None
    atenNumeroCliente: str | None = None
    atenNumeroSecundario: str | None = None
    atenAssunto: str | None = None
    atenDescricao: str | None = None
    atenDataAbertura: datetime | None = None
    atenDataRecepcao: datetime | None = None
    atenAnalistaCliente: str | None = None
    atenAnalistaInterno: str | None = None
    atenCausa: str | None = None
    atenSolucao: str | None = None
    atenObservacao: str | None = None
    atenTipo: AtenTipo | None = None


class AtendimentoResponse(AtendimentoBase):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(description="ObjectId do documento no MongoDB")


def doc_to_response(doc: dict[str, Any]) -> AtendimentoResponse:
    data = dict(doc)
    oid = data.pop("_id", None)
    if oid is None:
        raise ValueError("Documento sem _id")
    return AtendimentoResponse.model_validate({**data, "id": str(oid)})
