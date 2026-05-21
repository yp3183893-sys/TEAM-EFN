"""
tools.py — Herramientas para el agente CFDI/SAT
Base de datos: archivo .txt (cfdi_db.txt)
Formato de cada línea en cfdi_db.txt:
UUID|RFC_EMISOR|RFC_RECEPTOR|TOTAL|ESTADO|FECHA_VALIDACION|NOTA
"""

import os
from datetime import datetime
from langchain_core.tools import tool

# ── Ruta de la base de datos ─────────────────────────────────────────────────
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cfdi_db.txt"
)

SEPARADOR = "|"
CAMPOS = [
    "uuid",
    "rfc_emisor",
    "rfc_receptor",
    "total",
    "estado",
    "fecha_validacion",
    "nota",
]

# ── Helpers internos ─────────────────────────────────────────────────────────

def _leer_todos() -> list[dict]:
    """Lee el archivo .txt y devuelve lista de dicts."""
    if not os.path.exists(DB_PATH):
        return []

    registros = []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = linea.split(SEPARADOR)
            if len(partes) < len(CAMPOS):
                partes += [""] * (len(CAMPOS) - len(partes))
            registros.append(dict(zip(CAMPOS, partes)))
    return registros

def _escribir_todos(registros: list[dict]) -> None:
    """Sobreescribe el archivo con la lista de registros."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        f.write(
            "# CFDI Database — formato: UUID|RFC_EMISOR|RFC_RECEPTOR|TOTAL|ESTADO|FECHA_VALIDACION|NOTA\n"
        )
        for r in registros:
            linea = SEPARADOR.join(r.get(c, "") for c in CAMPOS)
            f.write(linea + "\n")

def _buscar_por_uuid(uuid: str) -> dict | None:
    """Devuelve el registro con ese UUID o None."""
    uuid = uuid.strip().upper()
    for r in _leer_todos():
        if r["uuid"].upper() == uuid:
            return r
    return None

# ── TOOL 2: Consultar CFDI en base de datos local ────────────────────────────

@tool
def consultar_cfdi(uuid: str) -> str:
    """
    Busca un CFDI previamente validado en la base de datos local (cfdi_db.txt).
    Útil para consultar el historial sin volver a llamar al SAT.
    Args:
        uuid: UUID del CFDI a consultar
    """
    registro = _buscar_por_uuid(uuid.strip())
    if not registro:
        return (
            f"UUID {uuid.strip().upper()} no encontrado en la base de datos local.\n"
            "Usa la tool `validar_cfdi_sat` para validarlo por primera vez."
        )

    return (
        f"Registro encontrado en base de datos.\n"
        f"UUID: {registro['uuid']}\n"
        f"RFC emisor: {registro['rfc_emisor']}\n"
        f"RFC receptor: {registro['rfc_receptor']}\n"
        f"Total: {registro['total']}\n"
        f"Estado: {registro['estado']}\n"
        f"Fecha validación: {registro['fecha_validacion']}\n"
        f"Nota: {registro['nota']}"
    )

# ── TOOL 3: Listar todos los CFDI validados ───────────────────────────────────

@tool
def listar_cfdi(filtro_estado: str = "") -> str:
    """
    Lista todos los CFDI registrados en la base de datos local.
    """
    registros = _leer_todos()
    if not registros:
        return "La base de datos está vacía."

    if filtro_estado:
        registros = [
            r for r in registros if r["estado"].lower() == filtro_estado.lower()
        ]

    lineas = [f"Total de registros: {len(registros)}\n"]
    for i, r in enumerate(registros, 1):
        lineas.append(
            f"{i}. UUID: {r['uuid']}\n"
            f"   Estado: {r['estado']}\n"
            f"   RFC emisor: {r['rfc_emisor']}\n"
            f"   RFC receptor: {r['rfc_receptor']}\n"
            f"   Total: {r['total']}\n"
            f"   Fecha: {r['fecha_validacion']}\n"
            f"   Nota: {r['nota']}\n"
        )

    return "\n".join(lineas)

# ── TOOL 4: Agregar nota de auditoría a un CFDI ───────────────────────────────

@tool
def agregar_nota_auditoria(uuid: str, nota: str) -> str:
    """
    Agrega o actualiza la nota de auditoría de un CFDI existente en la base de datos.
    Útil para registrar decisiones del contador, observaciones o acciones tomadas.
    Args:
        uuid: UUID del CFDI al que se agrega la nota
        nota: Texto de la nota de auditoría (máx. 300 caracteres)
    """
    uuid = uuid.strip().upper()
    nota = nota.strip()[:300]  # límite de seguridad

    registros = _leer_todos()
    encontrado = False
    for r in registros:
        if r["uuid"].upper() == uuid:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            # Concatena la nota anterior con la nueva (historial de notas)
            nota_anterior = r.get("nota", "")
            r["nota"] = (
                f"{nota_anterior} | [{timestamp}] {nota}"
                if nota_anterior
                else f"[{timestamp}] {nota}"
            )
            encontrado = True
            break

    if not encontrado:
        return (
            f"UUID {uuid} no encontrado en la base de datos.\n"
            "Primero valida el CFDI con `validar_cfdi_sat`."
        )

    _escribir_todos(registros)
    return (
        f"Nota de auditoría agregada correctamente.\n"
        f"UUID: {uuid}\n"
        f"Nota registrada: {nota}"
    )
