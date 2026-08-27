# agent/llm/openrouter_provider.py — Adaptador para OpenRouter
# Generado por AgentKit

"""
OpenRouter habla el formato de OpenAI (chat/completions), no el de Anthropic: por eso
este adaptador arma su propio request con httpx en vez de reusar el cliente de Anthropic.

Documentacion: https://openrouter.ai/docs
"""

import logging
import os

import httpx

from agent.llm.base import ErrorLLM, ProveedorLLM

logger = logging.getLogger("agentkit")

BASE_URL_POR_DEFECTO = "https://openrouter.ai/api/v1"


class ProveedorOpenRouter(ProveedorLLM):
    """Proveedor de IA usando OpenRouter."""

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        # Sin default: el slug cambia seguido y uno viejo tira 404. Se elige en la
        # entrevista contra https://openrouter.ai/models, no se inventa aca.
        self.modelo = os.getenv("OPENROUTER_MODEL", "").strip()
        # OpenRouter unifica el esfuerzo de razonamiento entre proveedores.
        # Dejalo vacio en el .env para no mandar el parametro.
        self.esfuerzo = os.getenv("OPENROUTER_EFFORT", "low").strip()
        self.max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS") or "4096")
        # Mismo cuidado que en zernio.py: os.getenv(clave, default) solo usa el default
        # si la clave NO existe. Como el .env trae "OPENROUTER_BASE_URL=" vacia, el "or"
        # es lo que hace que el default se aplique igual.
        self.base_url = (os.getenv("OPENROUTER_BASE_URL") or BASE_URL_POR_DEFECTO).rstrip("/")

        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY no esta configurada: el agente no va a poder responder")
        if not self.modelo:
            logger.warning(
                "OPENROUTER_MODEL no esta configurado: el agente no va a poder responder. "
                "Elegi un modelo en https://openrouter.ai/models"
            )

    async def generar(self, system_prompt: str, mensajes: list[dict]) -> str:
        if not self.api_key:
            raise ErrorLLM("Falta OPENROUTER_API_KEY")
        if not self.modelo:
            raise ErrorLLM("Falta OPENROUTER_MODEL")

        cuerpo = {
            "model": self.modelo,
            # OpenRouter usa el formato de OpenAI: el system prompt es un mensaje mas,
            # no un parametro aparte como en la API de Anthropic.
            "messages": [{"role": "system", "content": system_prompt}] + mensajes,
            "max_tokens": self.max_tokens,
        }
        if self.esfuerzo:
            cuerpo["reasoning"] = {"effort": self.esfuerzo}

        try:
            async with httpx.AsyncClient(timeout=60.0) as cliente:
                r = await cliente.post(
                    f"{self.base_url}/chat/completions",
                    json=cuerpo,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
        except httpx.HTTPError as e:
            raise ErrorLLM(f"Error de red hablando con OpenRouter: {e}") from e

        if r.status_code != 200:
            detalle = r.text[:500]
            try:
                detalle = (r.json().get("error") or {}).get("message", detalle)
            except ValueError:
                pass
            raise ErrorLLM(f"OpenRouter respondio {r.status_code}: {detalle}")

        datos = r.json()
        eleccion = (datos.get("choices") or [{}])[0]

        if eleccion.get("finish_reason") == "length":
            logger.warning(
                f"La respuesta se corto por llegar al tope de {self.max_tokens} tokens. "
                "Si pasa seguido, sube OPENROUTER_MAX_TOKENS o acorta el system prompt."
            )

        texto = ((eleccion.get("message") or {}).get("content") or "").strip()
        if not texto:
            logger.warning("OpenRouter devolvio una respuesta sin texto")
            return ""

        uso = datos.get("usage") or {}
        logger.info(
            f"Respuesta generada con {self.modelo} "
            f"({uso.get('prompt_tokens', '?')} in / {uso.get('completion_tokens', '?')} out)"
        )
        return texto
