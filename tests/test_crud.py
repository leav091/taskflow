from backend.server import crud
from backend.server.models import ItemCreate, ItemUpdate


def test_crud_round_trip_and_pagination(db):
    first = crud.create_item(db, ItemCreate(name="任务 🚀", description="中文描述"))
    item_id = first.id
    second = crud.create_item(db, ItemCreate(name="第二项"))
    assert [item.id for item in crud.get_items(db, skip=1, limit=1)] == [second.id]
    assert crud.get_item(db, item_id).description == "中文描述"
    updated = crud.update_item(db, item_id, ItemUpdate(name="已更新", description=None))
    assert updated.name == "已更新"
    assert updated.description is None
    assert crud.delete_item(db, item_id).id == item_id
    assert crud.get_item(db, item_id) is None


def test_missing_items(db):
    assert crud.get_item(db, 9999) is None
    assert crud.update_item(db, 9999, ItemUpdate(name="missing")) is None
    assert crud.delete_item(db, 9999) is None
