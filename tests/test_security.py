from datetime import UTC, datetime, timedelta

from src.security import can_cancel


def test_owner_within_24h():
    now = datetime.now(UTC)
    assert can_cancel("NEW", 1, 1, False, now - timedelta(hours=1), now)

def test_stranger_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 2, False, now, now)

def test_shipped_denied_even_admin():
    now = datetime.now(UTC)
    assert not can_cancel("SHIPPED", 1, 1, True, now, now)

def test_expired_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 1, False, now - timedelta(hours=25), now)


def test_admin_cancela_pedido_NEW_de_otro_usuario():
    now = datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
    assert can_cancel("NEW", owner_id=1, user_id=99, is_admin=True,
                      created_at=now - timedelta(days=3), now=now)

def test_propietario_exactamente_24h_denied():
    now = datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
    assert not can_cancel("NEW", owner_id=1, user_id=1, is_admin=False,
                          created_at=now - timedelta(hours=24), now=now)