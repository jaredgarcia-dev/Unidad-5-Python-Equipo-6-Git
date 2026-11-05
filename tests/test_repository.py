from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_repository_commit():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.commit()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120

def test_repository_commit_pedido_2_total_250():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(2, Order(250))
        session.commit()
        fila = session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert fila.id == 2 and fila.total == 250 and fila.status == "NEW"


def test_repository_rollback():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.rollback()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None
