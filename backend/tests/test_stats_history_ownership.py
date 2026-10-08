"""Offline ownership checks against actual routes and JWT authentication; no Atlas access."""
import copy
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

A, B = "fictional-A", "fictional-B"
ROWS = [
    dict(id="own", user_id=A, device_id=A, total_questions=5, correct_answers=2, category="test"),
    dict(id="migrated", user_id=A, device_id="old-guest", total_questions=5, correct_answers=3, category="test"),
    dict(id="other", user_id=B, device_id=A, total_questions=99, correct_answers=99, category="other"),
    dict(id="unowned", device_id=A, total_questions=88, correct_answers=88, category="other"),
]
class Cursor:
    def __init__(self, rows): self.rows=copy.deepcopy(rows)
    def sort(self, *args): return self
    def limit(self, n): self.rows=self.rows[:n]; return self
    async def to_list(self, n): return self.rows[:n]
class Attempts:
    def __init__(self): self.reads=[]
    def selected(self, query):
        self.reads.append(copy.deepcopy(query))
        assert query.get("user_id") in (A,B)
        assert "$or" not in query and "device_id" not in query
        return [r for r in ROWS if r.get("user_id")==query["user_id"]]
    def find(self, query, projection):
        assert projection == {"_id":0}
        return Cursor(self.selected(query))
    def aggregate(self, pipeline):
        rows=self.selected(pipeline[0]["$match"])
        if not rows: return Cursor([])
        result=dict(attempts=len(rows), total_q=sum(r["total_questions"] for r in rows),
                    total_correct=sum(r["correct_answers"] for r in rows))
        if "category" in pipeline[0]["$match"]:
            result.update(category=rows[0]["category"], pct=100*result["total_correct"]/result["total_q"])
        return Cursor([result])

@pytest.fixture
def setup(monkeypatch):
    attempts=Attempts()
    # Unexpected writes/other DB operations have no implementation and fail the test.
    monkeypatch.setattr(server,"db",SimpleNamespace(quiz_attempts=attempts))
    monkeypatch.setattr(server,"JWT_SECRET","isolated-test-key-not-production")
    return TestClient(server.app),attempts

def token(sub=A, **changes):
    payload={"sub":sub,"exp":datetime.now(timezone.utc)+timedelta(minutes=5)}
    payload.update(changes)
    return server.jwt.encode(payload,server.JWT_SECRET,algorithm=server.JWT_ALGORITHM)

def url(kind, identity=A):
    return "/api/stats/me?device_id="+identity if kind=="stats" else "/api/quiz-attempts/"+identity

@pytest.mark.parametrize("kind",["stats","history"])
@pytest.mark.parametrize("credential",["missing","garbage","expired","empty-sub","wrong-signature"])
def test_unauthorized_before_database(setup,kind,credential):
    client,db=setup
    value={"missing":None,"garbage":"invalid","expired":token(exp=datetime.now(timezone.utc)-timedelta(minutes=1)),
           "empty-sub":token(sub=""),"wrong-signature":server.jwt.encode({"sub":A},"wrong-test-key-for-isolated-hmac-check-only",algorithm=server.JWT_ALGORITHM)}[credential]
    response=client.get(url(kind),headers={"Authorization":"Bearer "+value} if value else {})
    assert response.status_code==401
    assert db.reads==[]

@pytest.mark.parametrize("kind",["stats","history"])
@pytest.mark.parametrize("requested",[B,"old-guest"])
def test_other_identity_forbidden_before_database(setup,kind,requested):
    client,db=setup
    response=client.get(url(kind,requested),headers={"Authorization":"Bearer "+token()})
    assert response.status_code==403
    assert db.reads==[]

@pytest.mark.parametrize("kind",["stats","history"])
def test_owner_and_migrated_rows_only(setup,kind):
    client,db=setup
    response=client.get(url(kind),headers={"Authorization":"Bearer "+token()})
    assert response.status_code==200
    data=response.json()
    if kind=="stats":
        assert data["overall"]==dict(attempts=2,total_q=10,total_correct=5,pct=50.0)
        assert set(data)=={"overall","by_category"}
    else:
        assert {r["id"] for r in data}=={"own","migrated"}
    assert all(q["user_id"]==A for q in db.reads)

@pytest.mark.parametrize("kind",["stats","history"])
def test_second_account_isolated(setup,kind):
    client,db=setup
    response=client.get(url(kind,B),headers={"Authorization":"Bearer "+token(sub=B)})
    assert response.status_code==200
    if kind=="history": assert [r["id"] for r in response.json()]==["other"]
    else: assert response.json()["overall"]["total_q"]==99
    assert all(q["user_id"]==B for q in db.reads)


def test_anonymous_quiz_submission_remains_available(monkeypatch):
    insert=AsyncMock()
    progress=AsyncMock()
    monkeypatch.setattr(server,"db",SimpleNamespace(
        quiz_attempts=SimpleNamespace(insert_one=insert),
        user_progress=SimpleNamespace(update_one=progress)))
    monkeypatch.setattr(server,"SEGMENT_WRITE_KEY",None)
    response=TestClient(server.app).post('/api/quiz-attempts',json={
        'device_id':'fictional-guest','client_attempt_id':'fictional-attempt',
        'mode':'daily','total_questions':5,'correct_answers':3,'score_percentage':60,
        'questions_answered':[],'started_at':'2026-10-08T10:00:00Z'})
    assert response.status_code==200
    assert response.json()['correct_answers']==3
    insert.assert_awaited_once()
    assert not insert.await_args.args[0].get('user_id')