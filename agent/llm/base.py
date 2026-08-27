# agent/llm/base.py — Clase base para proveedores de IA
# Generado por AgentKit

"""
Define la interfaz comun que todos los proveedores de IA implementan.
Gracias a esto, brain.py no sabe ni le importa si la respuesta vino de
Anthropic o de OpenRouter.
"""

from abc import ABC, abstractmethod


class ErrorLLM(Exception):
    """El proveedor de IA no pudo generar una respuesta (red, autenticacion, rate limit...)."""


class ProveedorLLM(ABC):
    """Interfaz que cada proveedor de IA debe implementar."""

    @abstractmethod
    async def generar(self, system_prompt: str, mensajes: list[dict]) -> str:
        """
        Genera una respuesta de texto.

        Args:
            system_prompt: quien es el agente y que sabe del negocio.
            mensajes: historial + mensaje nuevo, [{"role": "user"|"assistant", "content": "..."}]

        Returns:
            El texto de la respuesta, o "" si el modelo no genero texto util (brain.py
            lo trata como un caso de "no entendi", distinto de un error de la llamada).

        Raises:
            ErrorLLM: si la llamada en si fallo.
        """
        ...
