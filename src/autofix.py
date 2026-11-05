"""Reglas de AutoFix Pro (caso del Equipo 6, Unidad 3) trasladadas a código.

Regla 1 · US-06: si la cotización supera $5,000 MXN, el anticipo debe ser del 50%.
Regla 2 · US-02: cierre solo con vehículo reparado, pago completo y firma de conformidad.
Regla 3 · US-11: taller con 12 bahías y 8 cajones; la flotilla prioritaria tiene excepción.
"""

UMBRAL_ANTICIPO = 5000
PORCENTAJE_ANTICIPO = 0.5
BAHIAS = 12
CAJONES = 8


class AnticipoInsuficiente(Exception):
    pass


class CierreNoPermitido(Exception):
    pass


class CapacidadSaturada(Exception):
    pass


# Regla 1 (US-06)
def requiere_anticipo(monto):
    return monto > UMBRAL_ANTICIPO


def validar_anticipo(monto, anticipo_pagado):
    if requiere_anticipo(monto) and anticipo_pagado < monto * PORCENTAJE_ANTICIPO:
        raise AnticipoInsuficiente("anticipo del 50% requerido")
    return True


def cobrar_anticipo(gateway, monto):
    """Cobra el anticipo a través de una pasarela externa (se usa con mock en las pruebas)."""
    if not requiere_anticipo(monto):
        return 0.0
    anticipo = monto * PORCENTAJE_ANTICIPO
    if not gateway.charge(anticipo):
        raise RuntimeError("anticipo rechazado")
    return anticipo


# Regla 2 (US-02)
def cerrar_orden(reparado, pago_completo, firma_conformidad):
    if not (reparado and pago_completo and firma_conformidad):
        raise CierreNoPermitido("condición triple de cierre incompleta")
    return "CERRADA"


# Regla 3 (US-11)
class TallerCapacidad:
    def __init__(self):
        self.bahias = 0
        self.cajones = 0

    def ingresar(self, flotilla_prioritaria=False):
        if self.bahias < BAHIAS:
            self.bahias += 1
            return "BAHIA"
        if self.cajones < CAJONES:
            self.cajones += 1
            return "CAJON"
        if flotilla_prioritaria:
            return "EXCEPCION"
        raise CapacidadSaturada("taller al 100% de capacidad")
