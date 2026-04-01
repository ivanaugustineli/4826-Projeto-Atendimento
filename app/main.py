from datetime import datetime, timezone
from typing import Annotated, Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import FastAPI, HTTPException, Query, status
from pymongo import ReturnDocument

from app.database import get_db, lifespan, settings
from app.models import (
    AtendimentoBase,
    AtendimentoCreate,
    AtendimentoResponse,
    AtendimentoUpdate,
    doc_to_response,
)

app = FastAPI(
    title="Gerenciador de Atendimentos",
    version="0.1.0",
    lifespan=lifespan,
)


def parse_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id invalido (ObjectId)",
        ) from e


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/atendimentos",
    response_model=AtendimentoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def criar_atendimento(body: AtendimentoCreate) -> AtendimentoResponse:
    now = datetime.now(timezone.utc)
    abertura = body.atenDataAbertura or now
    recepcao = body.atenDataRecepcao or now

    doc: dict[str, Any] = {
        "atenNumeroCliente": body.atenNumeroCliente,
        "atenNumeroSecundario": body.atenNumeroSecundario,
        "atenAssunto": body.atenAssunto,
        "atenDescricao": body.atenDescricao,
        "atenDataAbertura": abertura,
        "atenDataRecepcao": recepcao,
        "atenAnalistaCliente": body.atenAnalistaCliente,
        "atenAnalistaInterno": body.atenAnalistaInterno,
        "atenCausa": body.atenCausa,
        "atenSolucao": body.atenSolucao,
        "atenObservacao": body.atenObservacao,
        "atenTipo": body.atenTipo.value,
    }
    if body.atenNumero is not None:
        doc["atenNumero"] = body.atenNumero
    else:
        doc["atenNumero"] = ""

    col = get_db()[settings.collection_name]
    result = await col.insert_one(doc)
    if body.atenNumero is None:
        await col.update_one(
            {"_id": result.inserted_id},
            {"$set": {"atenNumero": str(result.inserted_id)}},
        )

    saved = await col.find_one({"_id": result.inserted_id})
    if not saved:
        raise HTTPException(status_code=500, detail="Falha ao ler documento criado")
    return doc_to_response(saved)


@app.get("/atendimentos", response_model=list[AtendimentoResponse])
async def listar_atendimentos(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[AtendimentoResponse]:
    col = get_db()[settings.collection_name]
    cursor = col.find().skip(skip).limit(limit)
    out: list[AtendimentoResponse] = []
    async for raw in cursor:
        out.append(doc_to_response(raw))
    return out


@app.get("/atendimentos/{id}", response_model=AtendimentoResponse)
async def obter_atendimento(id: str) -> AtendimentoResponse:
    oid = parse_object_id(id)
    col = get_db()[settings.collection_name]
    doc = await col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    return doc_to_response(dict(doc))


@app.put("/atendimentos/{id}", response_model=AtendimentoResponse)
async def atualizar_atendimento(
    id: str,
    body: AtendimentoBase,
) -> AtendimentoResponse:
    oid = parse_object_id(id)
    col = get_db()[settings.collection_name]

    update_doc = {
        "atenNumero": body.atenNumero,
        "atenNumeroCliente": body.atenNumeroCliente,
        "atenNumeroSecundario": body.atenNumeroSecundario,
        "atenAssunto": body.atenAssunto,
        "atenDescricao": body.atenDescricao,
        "atenDataAbertura": body.atenDataAbertura,
        "atenDataRecepcao": body.atenDataRecepcao,
        "atenAnalistaCliente": body.atenAnalistaCliente,
        "atenAnalistaInterno": body.atenAnalistaInterno,
        "atenCausa": body.atenCausa,
        "atenSolucao": body.atenSolucao,
        "atenObservacao": body.atenObservacao,
        "atenTipo": body.atenTipo.value,
    }

    result = await col.find_one_and_update(
        {"_id": oid},
        {"$set": update_doc},
        return_document=ReturnDocument.AFTER,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    return doc_to_response(dict(result))


@app.patch("/atendimentos/{id}", response_model=AtendimentoResponse)
async def patch_atendimento(
    id: str,
    body: AtendimentoUpdate,
) -> AtendimentoResponse:
    oid = parse_object_id(id)
    col = get_db()[settings.collection_name]

    data = body.model_dump(exclude_unset=True)
    if not data:
        doc = await col.find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
        return doc_to_response(dict(doc))

    if "atenTipo" in data and data["atenTipo"] is not None:
        data["atenTipo"] = data["atenTipo"].value

    result = await col.find_one_and_update(
        {"_id": oid},
        {"$set": data},
        return_document=ReturnDocument.AFTER,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    return doc_to_response(dict(result))


@app.delete("/atendimentos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def excluir_atendimento(id: str) -> None:
    oid = parse_object_id(id)
    col = get_db()[settings.collection_name]
    deleted = await col.delete_one({"_id": oid})
    if deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
