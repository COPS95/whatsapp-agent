# agent/brain.py — Cerebro del agente: arma el prompt y llama al proveedor de IA
# Generado por AgentKit

"""
Logica de IA del agente. Lee el system prompt de config/prompts.yaml, arma el
historial y se lo pasa al proveedor de IA elegido (agent/llm/).
"""

import logging

import yaml
from dotenv import load_dotenv

from agent.llm import obtener_proveedor_llm
from agent.llm.base import ErrorLLM

load_dotenv()
logger = logging.getLogger("agentkit")

# Igual que con providers/obtener_proveedor() en main.py: si la configuracion esta mal,
# el servidor igual tiene que arrancar y contarlo, en vez de morirse en el import. Y hay
# que llamarlo DESPUES de load_dotenv(): este modulo se importa antes de que main.py
# corra su propio load_dotenv(), asi que si no se hace aca, los proveedores de agent/llm/
# leerian el .env vacio.
proveedor_llm = None
error_configuracion_llm: str | None = None
try:
    proveedor_llm = obtener_proveedor_llm()
except Exception as e:  # noqa: BLE001 — cualquier problema de configuracion
    error_configuracion_llm = str(e)


def cargar_config_prompts() -> dict:
    """Lee toda la configuracion desde config/prompts.yaml."""
    try:
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/prompts.yaml no encontrado")
        return {}


def cargar_system_prompt() -> str:
    """El system prompt: quien es el agente y que sabe del negocio."""
    return cargar_config_prompts().get(
        "system_prompt", "Eres un asistente util. Responde siempre en espanol."
    )


def obtener_mensaje_error() -> str:
    """Que decirle al cliente cuando algo falla de nuestro lado."""
    return cargar_config_prompts().get(
        "error_message",
        "Lo siento, estoy teniendo problemas tecnicos. Por favor intenta de nuevo en unos minutos.",
    )


def obtener_mensaje_fallback() -> str:
    """Que decirle al cliente cuando no se entendio el mensaje."""
    return cargar_config_prompts().get(
        "fallback_message", "Disculpa, no entendi tu mensaje. Podrias reformularlo?"
    )


async def generar_respuesta(mensaje: str, historial: list[dict]) -> tuple[str, bool]:
    """
    Genera una respuesta con el proveedor de IA configurado.

    Args:
        mensaje: el mensaje nuevo del cliente
        historial: los mensajes anteriores, [{"role": "user"|"assistant", "content": "..."}]

    Returns:
        (texto, es_respuesta_real)

        "es_respuesta_real" es False cuando lo que se devuelve es un aviso tecnico
        (error o fallback) y no una respuesta del agente. main.py lo usa para no
        guardar esos avisos en el historial: si se guardaran, quedarian contaminando
        el contexto de todos los mensajes siguientes.
    """
    if proveedor_llm is None:
        logger.error(f"Proveedor de IA no configurado: {error_configuracion_llm}")
        return obtener_mensaje_error(), False

    if not mensaje or len(mensaje.strip()) < 2:
        return obtener_mensaje_fallback(), False

    mensajes = [{"role": m["role"], "content": m["content"]} for m in historial]
    mensajes.append({"role": "user", "content": mensaje})

    system_prompt = cargar_system_prompt()

    try:
        texto = await proveedor_llm.generar(system_prompt, mensajes)
    except ErrorLLM as e:
        logger.error(f"Error llamando al proveedor de IA: {e}")
        return obtener_mensaje_error(), False

    if not texto:
        return obtener_mensaje_fallback(), False

    return texto, True
