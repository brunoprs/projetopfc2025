# app/test/test_models.py
import pytest
from sqlalchemy.exc import IntegrityError

def test_user_crud(db_session):
    from app.models import User
    u = User(username="ana", email="ana@ex.com", password_hash="x", name="Ana")
    db_session.add(u)
    db_session.commit()

    # read
    got = User.query.filter_by(email="ana@ex.com").first()
    assert got is not None
    assert got.username == "ana"

    # update
    got.name = "Ana Paula"
    db_session.commit()
    assert User.query.filter_by(name="Ana Paula").count() == 1

    # delete
    db_session.delete(got)
    db_session.commit()
    assert User.query.filter_by(email="ana@ex.com").count() == 0

def test_username_e_email_unicos(db_session):
    from app.models import User
    u1 = User(username="dup", email="dup@ex.com", password_hash="x", name="A")
    db_session.add(u1); db_session.commit()

    u2 = User(username="dup", email="other@ex.com", password_hash="y", name="B")
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    u3 = User(username="other", email="dup@ex.com", password_hash="z", name="C")
    db_session.add(u3)
    with pytest.raises(IntegrityError):
        db_session.commit()
