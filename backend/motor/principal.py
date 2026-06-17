from fastapi import FastAPI
from motor.api.rutas import router as motor_router

app = FastAPI(
    title="Servidor de Propagación ADS - Backend",
    description="Punto de acceso unificado con módulo de Motor EPiC encapsulado localmente."
)

app.include_router(motor_router)

# Comando para levantar el servidor: uvicorn motor.principal:app --reload
