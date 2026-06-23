# ============ PROMPT ============
# Crea la aplicación FastAPI principal del sistema ADS, integra los routers
# de motor y simulador como submódulos, habilita CORS para cualquier origen
# y define un endpoint GET / de health check con enlace a /docs.
# ======== FIN DEL PROMPT ========

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from motor.api import router as router_motor
from simulador.api import router as router_simulador

app = FastAPI(title="ADS — Motor + Simulador de Propagación Matricial", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_motor)
app.include_router(router_simulador)


@app.get("/")
def raiz():
    return {"status": "ok", "docs": "/docs"}
