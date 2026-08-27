# agent/llm/__init__.py — Factory de proveedores de IA
# Generado por AgentKit

"""
Elige el proveedor de IA segun la variable LLM_PROVIDER del .env.
"""

import os

from agent.llm.base import ErrorLLM, ProveedorLLM

PROVEEDORES_SOPORTADOS = ("anthropic", "openrouter")


def obtener_proveedor_llm() -> ProveedorLLM:
    """
    Retorna el proveedor de IA configurado en .env.

    Igual que agent/providers/obtener_proveedor() en main.py: esto NO se ejecuta al
    importar el modulo. Si la configuracion esta mal, el servidor igual tiene que
    arrancar y contarlo en el health check, en vez de morirse en el import.
    """
    proveedor = os.getenv("LLM_PROVIDER", "").strip().lower()

    if not proveedor:
        raise ValueError(
            "LLM_PROVIDER no esta configurado en el .env. "
            f"Valores validos: {' | '.join(PROVEEDORES_SOPORTADOS)}"
        )

    if proveedor == "anthropic":
        from agent.llm.anthropic_provider import ProveedorAnthropic

        return ProveedorAnthropic()

    if proveedor == "openrouter":
        from agent.llm.openrouter_provider import ProveedorOpenRouter

        return ProveedorOpenRouter()

    raise ValueError(
        f"Proveedor de IA no soportado: '{proveedor}'. "
        f"Valores validos: {' | '.join(PROVEEDORES_SOPORTADOS)}"
    )


__all__ = ["ErrorLLM", "ProveedorLLM", "PROVEEDORES_SOPORTADOS", "obtener_proveedor_llm"]
