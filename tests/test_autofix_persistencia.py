"""Integración con SQLAlchemy: el cierre de AutoFix se guarda y se confirma con commit."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.autofix import cerrar_orden
from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_af18_cierre_persistido_tras_commit():
    engine = make_engine()
    orden = Order(total=12000, status="CONFIRMED")
    with Session(engine) as session:
        orden.status = cerrar_orden(True, True, True)
        SqlOrderRepository(session).save(10, orden)
        session.commit()
        fila = session.scalar(select(OrderRow).where(OrderRow.id == 10))
        assert fila.status == "CERRADA"
        assert fila.total == 12000
