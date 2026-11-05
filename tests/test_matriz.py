"""Pruebas parametrizadas con csv.DictReader (ver LEEME: los CSV no se cargan solos)."""
import csv
from pathlib import Path
import pytest
from src.domain import Order, CustomerHasDebt

DATOS = Path(__file__).parent / "data" / "pedidos_prueba.csv"

# Resultado esperado por pedido_id, según la columna escenario del CSV
ESPERADO_COBRO = {"1": 120.0, "2": 170.0, "6": 850.0, "7": 0.01,
                  "9": 255.0, "10": 75.0, "12": 84.99}
ESPERADO_ERROR = {"3": (CustomerHasDebt, None), "11": (CustomerHasDebt, None),
                  "4": (ValueError, None), "5": (ValueError, None),
                  "8": (ValueError, "already confirmed")}

def cargar_filas():
    with DATOS.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

@pytest.mark.parametrize("fila", cargar_filas())
def test_matriz_pedidos(fila):
    pid = fila["pedido_id"]
    orden = Order(float(fila["total"]), vip=fila["es_vip"] == "1", status=fila["estado_inicial"])
    deuda = float(fila["deuda_cliente"])
    if pid in ESPERADO_COBRO:
        cobro = orden.confirm(customer_debt=deuda)
        assert abs(cobro - ESPERADO_COBRO[pid]) < 1e-9
        assert orden.status == "CONFIRMED"
    else:
        exc, mensaje = ESPERADO_ERROR[pid]
        with pytest.raises(exc, match=mensaje):
            orden.confirm(customer_debt=deuda)
