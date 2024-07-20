import datetime
import sys
import time
from unittest import mock

import pytest

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_lib.queue_items import QueueItem
from bec_lib.scan_data import ScanData
from bec_lib.scan_items import ScanItem
from bec_lib.scan_manager import ScanManager
from bec_lib.tests.utils import ConnectorMock

# pylint: disable=missing-function-docstring


@pytest.mark.parametrize(
    "queue_msg",
    [
        messages.ScanQueueStatusMessage(
            queue={
                "primary": {
                    "info": [
                        {
                            "queue_id": "7c15c9a2-71d4-4f2a-91a7-c4a63088fa38",
                            "scan_id": ["bfa582aa-f9cd-4258-ab5d-3e5d54d3dde5"],
                            "is_scan": [True],
                            "request_blocks": [
                                {
                                    "msg": b"\x84\xa8msg_type\xa4scan\xa7content\x83\xa9scan_type\xabfermat_scan\xa9parameter\x82\xa4args\x82\xa4samx\x92\xfe\x02\xa4samy\x92\xfe\x02\xa6kwargs\x83\xa4step\xcb?\xf8\x00\x00\x00\x00\x00\x00\xa8exp_time\xcb?\x94z\xe1G\xae\x14{\xa8relative\xc3\xa5queue\xa7primary\xa8metadata\x81\xa3RID\xd9$cd8fc68f-fe65-4031-9a37-e0e7ba9df542\xa7version\xcb?\xf0\x00\x00\x00\x00\x00\x00",
                                    "RID": "cd8fc68f-fe65-4031-9a37-e0e7ba9df542",
                                    "scan_motors": ["samx", "samy"],
                                    "is_scan": True,
                                    "scan_number": 25,
                                    "scan_id": "bfa582aa-f9cd-4258-ab5d-3e5d54d3dde5",
                                    "metadata": {"RID": "cd8fc68f-fe65-4031-9a37-e0e7ba9df542"},
                                    "content": {
                                        "scan_type": "fermat_scan",
                                        "parameter": {
                                            "args": {"samx": [-2, 2], "samy": [-2, 2]},
                                            "kwargs": {
                                                "step": 1.5,
                                                "exp_time": 0.02,
                                                "relative": True,
                                            },
                                        },
                                        "queue": "primary",
                                    },
                                }
                            ],
                            "scan_number": [25],
                            "status": "PENDING",
                            "active_request_block": None,
                        }
                    ],
                    "status": "RUNNING",
                }
            }
        )
    ],
)
def test_update_with_queue_status(queue_msg):
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.connector._get_buffer[MessageEndpoints.scan_queue_status().endpoint] = queue_msg
    scan_manager.update_with_queue_status(queue_msg)
    assert (
        scan_manager.scan_storage.find_scan_by_ID("bfa582aa-f9cd-4258-ab5d-3e5d54d3dde5")
        is not None
    )


def test_scan_item_to_pandas():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item.data = ScanData()
    data = {
        0: messages.ScanMessage(
            point_id=0, scan_id="scan_id", data={"samx": {"samx": {"value": 1, "timestamp": 0}}}
        ),
        1: messages.ScanMessage(
            point_id=1, scan_id="scan_id", data={"samx": {"samx": {"value": 2, "timestamp": 0}}}
        ),
        2: messages.ScanMessage(
            point_id=2, scan_id="scan_id", data={"samx": {"samx": {"value": 3, "timestamp": 0}}}
        ),
    }
    for ii, msg in data.items():
        scan_item.data.set(ii, msg)

    df = scan_item.to_pandas()
    assert df["samx"]["samx"]["value"].tolist() == [1, 2, 3]
    assert df["samx"]["samx"]["timestamp"].tolist() == [0, 0, 0]


def test_scan_item_to_pandas_empty_data():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item.data = ScanData()

    df = scan_item.to_pandas()
    assert df.empty


def test_scan_item_to_pandas_raises_without_pandas_installed():
    """Test that to_pandas raises an ImportError if pandas is not installed."""
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")

    with mock.patch.object(scan_item, "_get_pandas") as get_pandas:
        get_pandas.side_effect = ImportError
        with pytest.raises(ImportError):
            scan_item.to_pandas()


def test_scan_item_str():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    start_time = "Fri Jun 23 15:11:06 2023"
    # convert to datetime string to timestamp
    scan_item.start_time = time.mktime(
        datetime.datetime.strptime(start_time, "%a %b %d %H:%M:%S %Y").timetuple()
    )
    scan_item.end_time = scan_item.start_time + 10
    scan_item.num_points = 1
    assert (
        str(scan_item)
        == "ScanItem:\n \tStart time: Fri Jun 23 15:11:06 2023\n\tEnd time: Fri Jun 23 15:11:16"
        " 2023\n\tElapsed time: 10.0 s\n\tScan ID: ['scan_id']\n\tScan number: [1]\n\tNumber of"
        " points: 1\n"
    )


def test_scan_item_str_plain():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    assert str(scan_item) == "ScanItem:\n \tScan ID: ['scan_id']\n\tScan number: [1]\n"


def test_emit_data():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item.bec = mock.Mock()
    scan_item.bec.callbacks = mock.Mock()
    scan_item._run_request_callbacks = mock.Mock()
    msg = messages.ScanMessage(point_id=0, scan_id="scan_id", data={"samx": {"value": 1}})
    scan_item.emit_data(msg)
    scan_item.bec.callbacks.run.assert_called_once_with("scan_segment", msg.content, msg.metadata)
    scan_item._run_request_callbacks.assert_called_once_with(
        "scan_segment", msg.content, msg.metadata
    )


def test_emit_status():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item.bec = mock.Mock()
    scan_item.bec.callbacks = mock.Mock()
    scan_item._run_request_callbacks = mock.Mock()
    msg = messages.ScanStatusMessage(scan_id="scan_id", status="open", info={"info": "info"})
    scan_item.emit_status(msg)
    scan_item.bec.callbacks.run.assert_called_once_with("scan_status", msg.content, msg.metadata)
    scan_item._run_request_callbacks.assert_called_once_with(
        "scan_status", msg.content, msg.metadata
    )


def test_run_request_callbacks():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    queue_item = QueueItem(
        scan_manager, "queue_id", [{"RID": "requestID"}], "status", None, ["scan_id"]
    )
    with mock.patch("bec_lib.queue_items.update_queue") as mock_update_queue:
        with mock.patch.object(queue_item, "_update_with_buffer") as mock_update_buffer:
            with mock.patch.object(
                scan_manager.queue_storage, "find_queue_item_by_ID"
            ) as mock_find_queue:
                with mock.patch.object(
                    scan_manager.request_storage, "find_request_by_ID"
                ) as mock_find_req:
                    mock_find_queue.return_value = queue_item
                    scan_item._run_request_callbacks("event_type", "data", "metadata")
                    mock_find_req.return_value.callbacks.run.assert_called_once_with(
                        "event_type", "data", "metadata"
                    )


def test_poll_callbacks():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    queue_item = QueueItem(
        scan_manager, "queue_id", [{"RID": "requestID"}], "status", None, ["scan_id"]
    )
    with mock.patch("bec_lib.queue_items.update_queue") as mock_update_queue:
        with mock.patch.object(queue_item, "_update_with_buffer") as mock_update_buffer:
            with mock.patch.object(
                scan_manager.queue_storage, "find_queue_item_by_ID"
            ) as mock_find_queue:
                with mock.patch.object(
                    scan_manager.request_storage, "find_request_by_ID"
                ) as mock_find_req:
                    mock_find_queue.return_value = queue_item
                    scan_item.poll_callbacks()
                    mock_find_req.return_value.callbacks.poll.assert_called_once()


def test_scan_item_eq():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item1 = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item2 = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    assert scan_item1 == scan_item2


def test_scan_item_neq():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item1 = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item2 = ScanItem(scan_manager, "queue_id", [1], ["scan_id"], "status")
    scan_item2.scan_id = ["scan_id2"]
    assert scan_item1 != scan_item2


def test_update_with_scan_status_aborted():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.update_with_scan_status(
        messages.ScanStatusMessage(scan_id="", status="aborted", info={"info": "info"})
    )


def test_update_with_scan_status_last_scan_number():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        mock_find_scan.return_value = mock.MagicMock()
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(scan_id="scan_id", status="aborted", info={"scan_number": 1})
        )
        assert scan_manager.scan_storage.last_scan_number == 1


def test_update_with_scan_status_updates_start_time():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id", status="open", info={"scan_number": 1}, timestamp=10
            )
        )
        assert scan_item.start_time == 10


def test_update_with_scan_status_does_not_update_start_time():
    scan_manager = ScanManager(ConnectorMock(""))
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        mock_find_scan.return_value = scan_item
        scan_item.start_time = 0
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id", status="closed", info={"scan_number": 1}, timestamp=10
            )
        )
        assert scan_item.start_time == 0


def test_update_with_scan_status_updates_end_time():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id", status="closed", info={"scan_number": 1}, timestamp=10
            )
        )
        assert scan_item.end_time == 10


def test_update_with_scan_status_does_not_update_end_time():
    scan_manager = ScanManager(ConnectorMock(""))
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        mock_find_scan.return_value = scan_item
        scan_item.end_time = 0
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id", status="open", info={"scan_number": 1}, timestamp=10
            )
        )
        assert scan_item.end_time == 0


def test_update_with_scan_status_updates_num_points():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id",
                status="closed",
                info={"scan_number": 1, "num_points": 10},
                timestamp=10,
            )
        )
        assert scan_item.num_points == 10


def test_update_with_scan_status_updates_scan_number():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        scan_item.scan_number = None
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id",
                status="closed",
                info={"scan_number": 1, "num_points": 10},
                timestamp=10,
            )
        )
        assert scan_item.scan_number == 1


def test_update_with_scan_status_does_not_update_scan_number():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        scan_item.scan_number = 2
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id",
                status="closed",
                info={"scan_number": 1, "num_points": 10},
                timestamp=10,
            )
        )
        assert scan_item.scan_number == 2


def test_update_with_scan_status_adds_scan_def_id():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        scan_item.open_scan_defs = set()
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id",
                status="open",
                info={"scan_number": 1, "num_points": 10, "scan_def_id": "scan_def_id"},
                timestamp=10,
            )
        )
        assert "scan_def_id" in scan_item.open_scan_defs


def test_update_with_scan_status_removes_scan_def_id():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_manager.scan_storage.last_scan_number = 0
    with mock.patch.object(scan_manager.scan_storage, "find_scan_by_ID") as mock_find_scan:
        scan_item = mock.MagicMock()
        scan_item.open_scan_defs = set(["scan_def_id"])
        mock_find_scan.return_value = scan_item
        scan_manager.scan_storage.update_with_scan_status(
            messages.ScanStatusMessage(
                scan_id="scan_id",
                status="closed",
                info={"scan_number": 1, "num_points": 10, "scan_def_id": "scan_def_id"},
                timestamp=10,
            )
        )
        assert "scan_def_id" not in scan_item.open_scan_defs


def test_add_scan_segment_emits_data():
    scan_manager = ScanManager(ConnectorMock(""))
    scan_item = mock.MagicMock()
    scan_item.scan_id = "scan_id"
    scan_item.data = ScanData()
    scan_manager.scan_storage.storage.append(scan_item)

    msg = messages.ScanMessage(
        point_id=0, scan_id="scan_id", data={"samx": {"value": 1}}, metadata={"scan_id": "scan_id"}
    )
    scan_manager.scan_storage.add_scan_segment(msg)
    scan_item.emit_data.assert_called_once_with(msg)
    assert scan_item.data.messages == {0: msg}
