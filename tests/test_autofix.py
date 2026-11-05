"""Pruebas de las reglas de AutoFix Pro (Equipo 6). Ver tabla en el reporte, casos AF-01 a AF-17."""
from unittest.mock import Mock

import pytest

from src.autofix import (
    AnticipoInsuficiente,
    CapacidadSaturada,
    CierreNoPermitido,
    TallerCapacidad,
    cerrar_orden,
    cobrar_anticipo,
    requiere_anticipo,
    validar_anticipo,
)


# Regla 1 · US-06 anticipo del 50% si la cotización supera $5,000
def test_af01_monto_exacto_5000_no_requiere_anticipo():       # límite
    assert requiere_anticipo(5000) is False
    assert validar_anticipo(5000, 0) is True

def test_af02_monto_5001_con_anticipo_exacto_2500_50():       # límite
    assert validar_anticipo(5001, 2500.5) is True

def test_af03_monto_8000_con_anticipo_4000_es_valido():       # éxito
    assert validar_anticipo(8000, 4000) is True

def test_af04_monto_8000_con_anticipo_menor_al_50_falla():    # error
    with pytest.raises(AnticipoInsuficiente, match="50%"):
        validar_anticipo(8000, 3999.99)

def test_af05_monto_6000_sin_anticipo_falla():                # error
    with pytest.raises(AnticipoInsuficiente):
        validar_anticipo(6000, 0)

# Regla 2 · US-02 condición triple de cierre
def test_af06_cierre_con_las_tres_condiciones():              # éxito
    assert cerrar_orden(True, True, True) == "CERRADA"

def test_af07_cierre_sin_reparacion_falla():                  # error
    with pytest.raises(CierreNoPermitido):
        cerrar_orden(False, True, True)

def test_af08_cierre_sin_pago_completo_falla():               # error
    with pytest.raises(CierreNoPermitido):
        cerrar_orden(True, False, True)

def test_af09_cierre_sin_firma_falla():                       # error
    with pytest.raises(CierreNoPermitido):
        cerrar_orden(True, True, False)

# Regla 3 · US-11 capacidad 12 bahías y 8 cajones
def test_af10_primer_ingreso_va_a_bahia():                    # éxito
    assert TallerCapacidad().ingresar() == "BAHIA"

def test_af11_bahia_12_cupo_siguiente_va_a_cajon():           # límite
    taller = TallerCapacidad()
    for _ in range(12):
        taller.ingresar()
    assert taller.ingresar() == "CAJON"
    assert taller.cajones == 1

def test_af12_taller_lleno_sin_flotilla_rechaza():            # límite/error
    taller = TallerCapacidad()
    for _ in range(20):
        taller.ingresar()
    with pytest.raises(CapacidadSaturada):
        taller.ingresar()

def test_af13_taller_lleno_con_flotilla_prioritaria_tiene_excepcion():  # éxito de excepción
    taller = TallerCapacidad()
    for _ in range(20):
        taller.ingresar()
    assert taller.ingresar(flotilla_prioritaria=True) == "EXCEPCION"

# Integración simulada con pasarela de cobro (mock, sin cobros reales)
def test_af14_anticipo_aprobado_cobra_50_por_ciento():        # éxito con mock
    gateway = Mock()
    gateway.charge.return_value = True
    assert cobrar_anticipo(gateway, 8000) == 4000.0
    gateway.charge.assert_called_once_with(4000.0)

def test_af15_anticipo_rechazado_lanza_error():               # error con mock
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError, match="rechazado"):
        cobrar_anticipo(gateway, 8000)

def test_af16_timeout_de_pasarela_se_propaga():               # error con mock
    gateway = Mock()
    gateway.charge.side_effect = TimeoutError("pasarela sin respuesta")
    with pytest.raises(TimeoutError):
        cobrar_anticipo(gateway, 8000)

def test_af17_monto_bajo_no_llama_a_la_pasarela():            # límite con mock
    gateway = Mock()
    assert cobrar_anticipo(gateway, 5000) == 0.0
    gateway.charge.assert_not_called()
