from copy import deepcopy

import dotenv
from digitalhub_core.entities.artifacts.entity import Artifact

import digitalhub

dotenv.load_dotenv()


names = ["test1", "test2", "test3", "test4"]
uuids = [
    "12a01efa-o44f-4991-b153-9a3c358b7bb0",
    "8e367f52-25bb-4df1-b9c9-a58045b377a0",
    "1678f9ab-a2e0-48ff-870a-2384o3fa1334",
    "adb746dd-4e81-4ff8-82de-4916624o17dc",
]
paths = ["./data/test.csv", "s3://bucket/key.csv", "sql://database/schema/table", "https://url.com/file.csv"]
kind = ["artifact", "artifact", "artifact", "artifact"]

dicts = []
for i in range(len(names)):
    dicts.append({"name": names[i], "uuid": uuids[i], "path": paths[i], "kind": kind[i]})


digitalhub.delete_project("test")

p = digitalhub.get_or_create_project("test")

# Create and delete artifacts
for i in dicts:
    d = digitalhub.new_artifact(p.name, **i)
    digitalhub.delete_artifact(p.name, entity_id=d.id)
    d = digitalhub.new_artifact(p.name, **i)
    digitalhub.delete_artifact(p.name, entity_name=d.name)
    d = p.new_artifact(**i)
    p.delete_artifact(entity_id=d.id)

# Create multiple artifacts
for i in dicts:
    digitalhub.new_artifact(p.name, **i)

    c = deepcopy(i)
    c.pop("uuid")
    digitalhub.new_artifact(p.name, **c)
    digitalhub.new_artifact(p.name, **c)
    digitalhub.new_artifact(p.name, **c)
    digitalhub.new_artifact(p.name, **c)


# List artifacts
l_obj = digitalhub.list_artifacts(p.name)
assert isinstance(l_obj, list)
assert len(l_obj) == 4
for i in l_obj:
    assert isinstance(i, dict)

for uuid in uuids:
    digitalhub.delete_artifact(p.name, entity_id=uuid)

# Get artifacts test
for i in dicts:
    o1 = digitalhub.new_artifact(p.name, **i)
    assert isinstance(o1, Artifact)

    # Get by id
    o2 = digitalhub.get_artifact(p.name, entity_id=o1.id)
    assert isinstance(o2, Artifact)
    assert o1.id == o2.id

    # Get by name
    o3 = digitalhub.get_artifact(p.name, entity_name=o1.name)
    assert isinstance(o3, Artifact)
    assert o1.id == o3.id

    # Get by name as latest
    c = deepcopy(i)
    c.pop("uuid")
    o4 = digitalhub.new_artifact(p.name, **c)
    o5 = digitalhub.get_artifact(p.name, entity_name=o1.name)
    assert isinstance(o5, Artifact)
    assert (o5.id != o1.id) and (o5.name == o1.name) and (o5.id == o4.id)


# Delete artifacts, all versions
for n in names:
    digitalhub.delete_artifact(p.name, entity_name=n, delete_all_versions=True)
l_obj = digitalhub.list_artifacts(p.name)
assert not l_obj

digitalhub.delete_project("test")
