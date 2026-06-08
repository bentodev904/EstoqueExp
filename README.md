# 🧩 Estoque Clínica — Deploy Railway

Sistema de controle de estoque com QR Code para clínicas.

## Deploy em 5 minutos

### 1. Suba o backend no Railway

1. Crie conta gratuita em **railway.app**
2. Clique **New Project → Deploy from GitHub repo**
3. Faça upload da pasta `backend/` como repositório **ou** use o Railway CLI:
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```
4. Railway detecta o `Procfile` automaticamente e faz o deploy
5. Vá em **Settings → Networking → Generate Domain** para obter a URL pública

> URL ficará tipo: `https://clinica-estoque-production.up.railway.app`

### 2. Configure o frontend

Abra o arquivo `frontend/index.html` em qualquer navegador.

Na primeira vez, um banner amarelo pedirá a URL do backend.  
Cole a URL do Railway e clique **Salvar**.

A URL fica salva no navegador — qualquer dispositivo que acessar o HTML e configurar a mesma URL verá os mesmos dados em tempo real.

### 3. Distribuir para os funcionários

Opção A — Arquivo compartilhado:
- Coloque o `index.html` numa pasta do Google Drive compartilhada
- Cada funcionário abre no celular/PC e configura a URL uma vez só

Opção B — Hospedar o frontend também no Railway:
- Copie `index.html` para `backend/static/index.html`
- O FastAPI serve o arquivo automaticamente
- Acesse direto pela URL do Railway

## Estrutura

```
backend/
  main.py          # API FastAPI (SQLite)
  requirements.txt
  Procfile
  railway.toml

frontend/
  index.html       # App completo (abre em qualquer navegador)
```

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/items | Listar itens |
| POST | /api/items | Criar item |
| PUT | /api/items/{id} | Editar item |
| DELETE | /api/items/{id} | Remover item |
| GET | /api/loans | Listar empréstimos |
| POST | /api/loans | Registrar empréstimo |
| POST | /api/loans/{id}/return | Registrar devolução |
| GET | /docs | Swagger UI automático |

## Custo

- **Railway Free Tier**: 500h/mês grátis (suficiente para uso contínuo)
- **Etiquetas**: papel comum + impressora qualquer — QR Code gerado pelo sistema
- **Celulares**: câmera nativa via navegador, sem app adicional
