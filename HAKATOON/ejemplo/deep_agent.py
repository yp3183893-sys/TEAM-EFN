import os
import sys
from typing import List

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool

# =========================================================
# CONFIGURACIÓN
# =========================================================

load_dotenv(".env")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.tools import (
    agregar_nota_auditoria,
    consultar_cfdi,
    listar_cfdi,
)
from tools.validar_factura import validar_cfdi_sat

# =========================================================
# LISTA SIMPLE DE TAREAS
# =========================================================

tareas = []


def agregar_tareas(lista):
    for tarea in lista:
        tareas.append({"descripcion": tarea, "estado": "pendiente"})


def completar_tarea(indice):
    tareas[indice]["estado"] = "completada"


def hay_tareas_pendientes():
    for tarea in tareas:
        if tarea["estado"] == "pendiente":
            return True

    return False


def ver_tareas():
    texto = "\nLISTA DE TAREAS:\n"

    for i, tarea in enumerate(tareas):
        texto += f"{i}. [{tarea['estado']}] {tarea['descripcion']}\n"

    return texto


# =========================================================
# TOOLS
# =========================================================


@tool
def planificar_tareas(lista: List[str]):
    """
    Crea una lista de tareas.
    """

    agregar_tareas(lista)

    return f"Se agregaron {len(lista)} tareas."


@tool
def actualizar_tarea(indice: int):
    """
    Marca una tarea como completada.
    """

    completar_tarea(indice)

    return f"Tarea {indice} completada."


@tool
def ver_lista_tareas():
    """
    Muestra todas las tareas.
    """

    return ver_tareas()


# =========================================================
# PROMPT DEL AGENTE
# =========================================================

PROMPT_SISTEMA = """
Eres un agente autónomo de auditoría CFDI.

Tu trabajo es:

1. Crear un plan de tareas
2. Ejecutar cada tarea
3. Marcar las tareas como completadas
4. Continuar automáticamente hasta terminar

REGLAS:

- Primero usa planificar_tareas
- Después ejecuta las tareas una por una
- Después de cada tarea usa actualizar_tarea
- Solo da una respuesta final cuando TODO esté terminado

Herramientas disponibles:

- planificar_tareas
- actualizar_tarea
- ver_lista_tareas
- listar_cfdi
- consultar_cfdi
- validar_cfdi_sat
- agregar_nota_auditoria
"""

# =========================================================
# HERRAMIENTAS
# =========================================================

HERRAMIENTAS = [
    planificar_tareas,
    actualizar_tarea,
    ver_lista_tareas,
    listar_cfdi,
    consultar_cfdi,
    validar_cfdi_sat,
    agregar_nota_auditoria,
]

# Diccionario:
# "nombre_tool" -> tool real

MAPA_HERRAMIENTAS = {tool.name: tool for tool in HERRAMIENTAS}

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    consulta_usuario = """
    Audita todas mis facturas. 
    Valídalas con el SAT y agrega notas si encuentras anomalías.
    """
    
    # =====================================================
    # MODELO
    # =====================================================

    modelo = init_chat_model(model="openai:gpt-4o-mini", temperature=0)

    agente = modelo.bind_tools(HERRAMIENTAS)

    # =====================================================
    # MENSAJES
    # =====================================================

    mensajes = [
        SystemMessage(content=PROMPT_SISTEMA),
        HumanMessage(content=consulta_usuario),
    ]

    # =====================================================
    # LOOP DEL AGENTE
    # =====================================================

    for iteracion in range(20):
        print(f"\n========== ITERACIÓN {iteracion} ==========\n")

        respuesta = agente.invoke(mensajes)

        mensajes.append(respuesta)

        # -------------------------------------------------
        # ¿EL AGENTE QUIERE USAR TOOLS?
        # -------------------------------------------------

        if respuesta.tool_calls:
            for tool_call in respuesta.tool_calls:
                nombre = tool_call["name"]
                args = tool_call["args"]

                print(f"Tool: {nombre}")
                print(f"Args: {args}")

                herramienta = MAPA_HERRAMIENTAS[nombre]

                try:
                    resultado = herramienta.invoke(args)

                except Exception as e:
                    resultado = f"ERROR: {e}"

                print(f"Resultado: {resultado}\n")

                mensajes.append(
                    ToolMessage(content=str(resultado), tool_call_id=tool_call["id"])
                )

        # -------------------------------------------------
        # RESPUESTA FINAL
        # -------------------------------------------------

        else:
            # Si todavía hay tareas pendientes,
            # obligamos al agente a continuar

            if hay_tareas_pendientes():
                print("Aún hay tareas pendientes...\n")

                mensajes.append(
                    HumanMessage(
                        content=(
                            "Todavía tienes tareas pendientes. Continúa trabajando."
                        )
                    )
                )

                continue

            print("RESPUESTA FINAL")

            print(respuesta.content)

            break