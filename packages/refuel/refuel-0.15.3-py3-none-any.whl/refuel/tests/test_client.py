test_task_name = "cricket_classification_sdk"

test_task_id = "105816f8-b977-46a1-bd7f-def3f9e535d9"

test_dataset_name = "cricket_commentary"

test_dataset_id = "0d65f84c-ded5-4b48-b271-6a32663ca427"

test_project_name = "test_sdk"

test_project_id = "0aff3ec6-bca9-4245-9b40-2524d607a07c"

test_items_filter = {
    "field": "commentary_short",
    "operator": "ILIKE",
    "value": "run",
}


def test_client_init(refuel_client):
    assert refuel_client is not None
    assert refuel_client._project_id == test_project_id
    return


# Get Items (no task)
def test_get_items_no_task(refuel_client):
    items = refuel_client.get_items(dataset=test_dataset_name)
    assert len(items) == 20
    return


# Get Items (with task)
def test_get_items_with_task(refuel_client):
    items = refuel_client.get_items(dataset=test_dataset_name, task=test_task_name)
    assert len(items) == 20
    return


# Get Items (large max_items + offset)
def test_large_get_items(refuel_client):
    items = refuel_client.get_items(
        dataset=test_dataset_name,
        task=test_task_name,
        max_items=300,
        offset=200,
    )
    assert len(items) == 300
    return


# Get Items (with filter)
def test_filtered_get_items(refuel_client):
    items = refuel_client.get_items(
        dataset=test_dataset_name,
        task=test_task_name,
        filters=[test_items_filter],
    )
    for k, v in items[test_items_filter["field"]].items():
        assert test_items_filter["value"] in v
    return


# Get Items order ascend
def test_get_items_order_ascend(refuel_client):
    items = refuel_client.get_items(
        dataset=test_dataset_name,
        task=test_task_name,
        order_by=[{"field": "bowler_name", "direction": "ASC"}],
    )
    assert items is not None
    names = items["bowler_name"].tolist()
    assert all(names[i] <= names[i + 1] for i in range(len(names) - 1))
    return


# Get Items order descend
def test_get_items_order_descend(refuel_client):
    items = refuel_client.get_items(
        dataset=test_dataset_name,
        task=test_task_name,
        order_by=[{"field": "bowler_name", "direction": "DESC"}],
    )
    assert items is not None
    names = items["bowler_name"].tolist()
    assert all(names[i] >= names[i + 1] for i in range(len(names) - 1))
    return


def test_get_datasets(refuel_client):
    datasets = refuel_client.get_datasets()
    assert datasets is not None
    return


def test_get_dataset(refuel_client):
    dataset = refuel_client.get_dataset(test_dataset_name)
    assert dataset is not None
    assert dataset["id"] == test_dataset_id
    return


def test_get_projects(refuel_client):
    projects = refuel_client.get_projects()
    assert projects is not None
    return


def test_get_project(refuel_client):
    project = refuel_client.get_project(test_project_name)
    assert project["id"] == test_project_id
    return


def test_get_tasks(refuel_client):
    tasks = refuel_client.get_tasks()
    assert tasks is not None
    return


def test_get_task(refuel_client):
    task = refuel_client.get_task(task=test_task_name)
    assert task is not None
    assert task["id"] == test_task_id
    return


def test_get_task_run(refuel_client):
    task_run = refuel_client.get_task_run(
        task=test_task_name, dataset=test_dataset_name
    )
    assert task_run is not None
    assert task_run["task_id"] == test_task_id
    assert task_run["dataset_id"] == test_dataset_id
    assert task_run["project_id"] == test_project_id
    return


# Upload Dataset
# TODO

# Download Dataset
# TODO

# Start Labeling Task Run
# TODO

# Cancel Labeling Task Run
# TODO
