# Gerenciador de Atendimentos de Sustentacao

Aplicacao web de suporte tecnico com:
- **FastAPI** (API Python assincrona)
- **MongoDB** (persistencia)
- **Nginx** (proxy reverso + frontend estatico)
- Execucao **100% via Docker Compose**

## Arquitetura

- `db`: MongoDB com volume persistente
- `app`: API FastAPI (Uvicorn)
- `web`: Nginx servindo frontend e roteando `/api/*` para a API

## Leiaute de Diretorios

```text
.
├── .cursorrules
├── .env
├── Dockerfile
├── docker-compose.yml
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── requirements.txt
├── nginx/
│   └── default.conf
└── static/
    └── index.html
```

## Variaveis de Ambiente

Arquivo `.env`:

```env
MONGODB_URI=mongodb://db:27017
MONGODB_DB=atendimentos_db
COLLECTION_NAME=atendimentos
```

## Como executar

Na raiz do projeto:

```bash
docker compose up --build
```

Endpoints principais:
- Frontend: `http://localhost/`
- Swagger: `http://localhost/api/docs`
- Healthcheck: `http://localhost/api/health`

## CRUD de Atendimentos

Base path da API no ambiente com Nginx: `/api`

- `POST /api/atendimentos`
- `GET /api/atendimentos`
- `GET /api/atendimentos/{id}`
- `PUT /api/atendimentos/{id}`
- `PATCH /api/atendimentos/{id}`
- `DELETE /api/atendimentos/{id}`

## Exemplo de inclusao (PowerShell)

```powershell
$body = @{
  atenNumero = "AT0001"
  atenNumeroCliente = "PRB0069090"
  atenNumeroSecundario = ""
  atenAssunto = "Problema Teste"
  atenDescricao = "Texto do problema teste."
  atenDataAbertura = "2026-04-01T11:26:54.376Z"
  atenDataRecepcao = "2026-04-01T11:26:54.376Z"
  atenAnalistaCliente = "FULANO DE TAL"
  atenAnalistaInterno = "CICLANO DA SILVA"
  atenCausa = ""
  atenSolucao = ""
  atenObservacao = ""
  atenTipo = "PRB"
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Method Post -Uri "http://localhost/api/atendimentos" -ContentType "application/json" -Body $body
```

## Observacoes

- Nao e necessario instalar Python/MongoDB no host.
- Toda execucao e dependencia ficam isoladas no Docker.
