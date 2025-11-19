from fastapi import FastAPI
from langserve import add_routes
from app import chain_with_history

app = FastAPI(
    title="Meu Pisicologo - IA",
    description="Deixe o Psicologo ajudar você. Faça uma pergunta!"
)

# expor a chain como API
add_routes(app, chain_with_history, path="/assistente")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=9000)
