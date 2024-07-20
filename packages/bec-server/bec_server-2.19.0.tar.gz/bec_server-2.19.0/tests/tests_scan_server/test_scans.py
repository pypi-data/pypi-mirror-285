import collections
import inspect
from unittest import mock

import numpy as np
import pytest

from bec_lib import messages
from bec_server.device_server.tests.utils import DMMock
from bec_server.scan_server.errors import ScanAbortion
from bec_server.scan_server.scan_plugins.otf_scan import OTFScan
from bec_server.scan_server.scans import (
    Acquire,
    AddInteractiveScanPoint,
    CloseInteractiveScan,
    ContLineFlyScan,
    ContLineScan,
    DeviceRPC,
    FermatSpiralScan,
    LineScan,
    ListScan,
    MonitorScan,
    Move,
    OpenInteractiveScan,
    RequestBase,
    RoundROIScan,
    RoundScan,
    RoundScanFlySim,
    Scan,
    ScanBase,
    TimeScan,
    UpdatedMove,
    get_2D_raster_pos,
    get_fermat_spiral_pos,
    get_round_roi_scan_positions,
    get_round_scan_positions,
    unpack_scan_args,
)

# pylint: disable=missing-function-docstring
# pylint: disable=protected-access


def test_unpack_scan_args_empty_dict():
    scan_args = {}
    expected_args = []
    assert unpack_scan_args(scan_args) == expected_args


def test_unpack_scan_args_non_dict_input():
    scan_args = [1, 2, 3]
    assert unpack_scan_args(scan_args) == scan_args


def test_unpack_scan_args_valid_input():
    scan_args = {"cmd1": [1, 2, 3], "cmd2": ["a", "b", "c"]}
    expected_args = ["cmd1", 1, 2, 3, "cmd2", "a", "b", "c"]
    assert unpack_scan_args(scan_args) == expected_args


@pytest.mark.parametrize(
    "mv_msg,reference_msg_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="mv",
                parameter={"args": {"samx": (1,), "samy": (2,)}, "kwargs": {}},
                queue="primary",
            ),
            [
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 1, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 0, "response": True},
                ),
                messages.DeviceInstructionMessage(
                    device="samy",
                    action="set",
                    parameter={"value": 2, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 1, "response": True},
                ),
            ],
        ),
        (
            messages.ScanQueueMessage(
                scan_type="mv",
                parameter={"args": {"samx": (1,), "samy": (2,), "samz": (3,)}, "kwargs": {}},
                queue="primary",
            ),
            [
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 1, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 0, "response": True},
                ),
                messages.DeviceInstructionMessage(
                    device="samy",
                    action="set",
                    parameter={"value": 2, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 1, "response": True},
                ),
                messages.DeviceInstructionMessage(
                    device="samz",
                    action="set",
                    parameter={"value": 3, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 2, "response": True},
                ),
            ],
        ),
        (
            messages.ScanQueueMessage(
                scan_type="mv", parameter={"args": {"samx": (1,)}, "kwargs": {}}, queue="primary"
            ),
            [
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 1, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 0, "response": True},
                )
            ],
        ),
    ],
)
def test_scan_move(mv_msg, reference_msg_list):
    msg_list = []
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samy")
    device_manager.add_device("samz")

    def offset_mock():
        yield None

    s = Move(parameter=mv_msg.content.get("parameter"), device_manager=device_manager)
    s._set_position_offset = offset_mock
    for step in s.run():
        if step:
            msg_list.append(step)

    assert msg_list == reference_msg_list


@pytest.mark.parametrize(
    "mv_msg, reference_msg_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="umv",
                parameter={"args": {"samx": (1,), "samy": (2,)}, "kwargs": {}},
                queue="primary",
                metadata={"RID": "0bab7ee3-b384-4571-b...0fff984c05"},
            ),
            [
                messages.DeviceInstructionMessage(
                    device=None,
                    action="scan_report_instruction",
                    parameter={
                        "readback": {
                            "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                            "devices": ["samx", "samy"],
                            "start": [0, 0],
                            "end": np.array([1.0, 2.0]),
                        }
                    },
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 0,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 1.0, "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 1,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samy",
                    action="set",
                    parameter={"value": 2.0, "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 2,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="wait",
                    parameter={"type": "move", "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 3,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samy",
                    action="wait",
                    parameter={"type": "move", "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 4,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
            ],
        ),
        (
            messages.ScanQueueMessage(
                scan_type="umv",
                parameter={"args": {"samx": (1,), "samy": (2,), "samz": (3,)}, "kwargs": {}},
                queue="primary",
                metadata={"RID": "0bab7ee3-b384-4571-b...0fff984c05"},
            ),
            [
                messages.DeviceInstructionMessage(
                    device=None,
                    action="scan_report_instruction",
                    parameter={
                        "readback": {
                            "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                            "devices": ["samx", "samy", "samz"],
                            "start": [0, 0, 0],
                            "end": np.array([1.0, 2.0, 3.0]),
                        }
                    },
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 0,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 1.0, "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 1,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samy",
                    action="set",
                    parameter={"value": 2.0, "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 2,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samz",
                    action="set",
                    parameter={"value": 3.0, "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 3,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="wait",
                    parameter={"type": "move", "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 4,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samy",
                    action="wait",
                    parameter={"type": "move", "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 5,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samz",
                    action="wait",
                    parameter={"type": "move", "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 6,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
            ],
        ),
        (
            messages.ScanQueueMessage(
                scan_type="umv",
                parameter={"args": {"samx": (1,)}, "kwargs": {}},
                queue="primary",
                metadata={"RID": "0bab7ee3-b384-4571-b...0fff984c05"},
            ),
            [
                messages.DeviceInstructionMessage(
                    device=None,
                    action="scan_report_instruction",
                    parameter={
                        "readback": {
                            "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                            "devices": ["samx"],
                            "start": [0],
                            "end": np.array([1.0]),
                        }
                    },
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 0,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 1.0, "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 1,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="wait",
                    parameter={"type": "move", "wait_group": "scan_motor"},
                    metadata={
                        "readout_priority": "monitored",
                        "DIID": 2,
                        "RID": "0bab7ee3-b384-4571-b...0fff984c05",
                    },
                ),
            ],
        ),
    ],
)
def test_scan_updated_move(mv_msg, reference_msg_list):
    msg_list = []
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samy")
    device_manager.add_device("samz")

    s = UpdatedMove(
        parameter=mv_msg.content.get("parameter"),
        device_manager=device_manager,
        metadata=mv_msg.metadata,
    )

    with mock.patch.object(s.stubs, "_get_from_rpc") as mock_get_from_rpc:
        # set reading to expected start values from scan_report_instruction
        mock_get_from_rpc.return_value = {
            dev: {"value": value}
            for dev, value in zip(
                reference_msg_list[0].content["parameter"]["readback"]["devices"],
                reference_msg_list[0].content["parameter"]["readback"]["start"],
            )
        }

        def mock_rpc_func(*args, **kwargs):
            yield None

        with mock.patch.object(s.stubs, "rpc") as mock_rpc:
            mock_rpc.side_effect = mock_rpc_func
            for step in s.run():
                if step:
                    msg_list.append(step)

        assert msg_list == reference_msg_list


@pytest.mark.parametrize(
    "scan_msg,reference_scan_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="grid_scan",
                parameter={"args": {"samx": (-5, 5, 3)}, "kwargs": {}},
                queue="primary",
            ),
            [
                messages.DeviceInstructionMessage(
                    device=["samx"],
                    action="read",
                    parameter={"wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 3},
                ),
                messages.DeviceInstructionMessage(
                    device=["samx"],
                    action="wait",
                    parameter={"type": "read", "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 4},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="open_scan",
                    parameter={
                        "scan_motors": ["samx"],
                        "readout_priority": {
                            "monitored": ["samx"],
                            "baseline": [],
                            "on_request": [],
                            "async": [],
                        },
                        "num_points": 3,
                        "positions": [[-5.0], [0.0], [5.0]],
                        "scan_name": "grid_scan",
                        "scan_type": "step",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 0},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="stage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 1},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="baseline_reading",
                    parameter={},
                    metadata={"readout_priority": "baseline", "DIID": 1},
                ),
                messages.DeviceInstructionMessage(
                    **{
                        "device": "samx",
                        "action": "set",
                        "parameter": {"value": -5.0, "wait_group": "scan_motor"},
                    },
                    metadata={"readout_priority": "monitored", "DIID": 8},
                ),
                messages.DeviceInstructionMessage(
                    **{
                        "device": None,
                        "action": "wait",
                        "parameter": {
                            "type": "move",
                            "group": "scan_motor",
                            "wait_group": "scan_motor",
                        },
                    },
                    metadata={"readout_priority": "monitored", "DIID": 9},
                ),
                messages.DeviceInstructionMessage(
                    **{"device": None, "action": "pre_scan", "parameter": {}},
                    metadata={"readout_priority": "monitored", "DIID": 7},
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": -5.0, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 1},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 2},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"point_id": 0, "readout_priority": "monitored", "DIID": 3},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "group": "trigger", "time": 0},
                    metadata={"readout_priority": "monitored", "DIID": 4},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"point_id": 0, "readout_priority": "monitored", "DIID": 5},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={
                        "type": "read",
                        "group": "scan_motor",
                        "wait_group": "readout_primary",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 6},
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 0.0, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 7},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 8},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 9},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"point_id": 1, "readout_priority": "monitored", "DIID": 10},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "group": "trigger", "time": 0},
                    metadata={"readout_priority": "monitored", "DIID": 11},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"point_id": 1, "readout_priority": "monitored", "DIID": 12},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={
                        "type": "read",
                        "group": "scan_motor",
                        "wait_group": "readout_primary",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 13},
                ),
                messages.DeviceInstructionMessage(
                    device="samx",
                    action="set",
                    parameter={"value": 5.0, "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 14},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 15},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 16},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"point_id": 2, "readout_priority": "monitored", "DIID": 17},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "group": "trigger", "time": 0},
                    metadata={"readout_priority": "monitored", "DIID": 18},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"point_id": 2, "readout_priority": "monitored", "DIID": 19},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={
                        "type": "read",
                        "group": "scan_motor",
                        "wait_group": "readout_primary",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 20},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 23},
                ),
                messages.DeviceInstructionMessage(
                    **{"device": None, "action": "complete", "parameter": {}},
                    metadata={"readout_priority": "monitored", "DIID": 31},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="unstage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 24},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="close_scan",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 25},
                ),
            ],
        )
    ],
)
def test_scan_scan(scan_msg, reference_scan_list):
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.devices["samx"].read_buffer = {"value": 0}
    msg_list = []

    def offset_mock():
        yield None

    scan = Scan(parameter=scan_msg.content.get("parameter"), device_manager=device_manager)
    scan._set_position_offset = offset_mock
    for step in scan.run():
        if step:
            msg_list.append(step)
    scan_uid = msg_list[0].metadata.get("scan_id")
    for ii, _ in enumerate(reference_scan_list):
        if reference_scan_list[ii].metadata.get("scan_id") is not None:
            reference_scan_list[ii].metadata["scan_id"] = scan_uid
        reference_scan_list[ii].metadata["DIID"] = ii
    assert msg_list == reference_scan_list


@pytest.mark.parametrize(
    "scan_msg,reference_scan_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="fermat_scan",
                parameter={"args": {"samx": (-5, 5), "samy": (-5, 5)}, "kwargs": {"step": 3}},
                queue="primary",
            ),
            [
                (0, np.array([-1.1550884, -1.26090078])),
                (1, np.array([2.4090456, 0.21142208])),
                (2, np.array([-2.35049217, 1.80207841])),
                (3, np.array([0.59570227, -3.36772012])),
                (4, np.array([2.0522743, 3.22624707])),
                (5, np.array([-4.04502068, -1.08738572])),
                (6, np.array([4.01502502, -2.08525157])),
                (7, np.array([-1.6591442, 4.54313114])),
                (8, np.array([-1.95738438, -4.7418927])),
                (9, np.array([4.89775337, 2.29194501])),
            ],
        ),
        (
            messages.ScanQueueMessage(
                scan_type="fermat_scan",
                parameter={
                    "args": {"samx": (-5, 5), "samy": (-5, 5)},
                    "kwargs": {"step": 3, "spiral_type": 1},
                },
                queue="primary",
            ),
            [
                (0, np.array([1.1550884, 1.26090078])),
                (1, np.array([2.4090456, 0.21142208])),
                (2, np.array([2.35049217, -1.80207841])),
                (3, np.array([0.59570227, -3.36772012])),
                (4, np.array([-2.0522743, -3.22624707])),
                (5, np.array([-4.04502068, -1.08738572])),
                (6, np.array([-4.01502502, 2.08525157])),
                (7, np.array([-1.6591442, 4.54313114])),
                (8, np.array([1.95738438, 4.7418927])),
                (9, np.array([4.89775337, 2.29194501])),
            ],
        ),
    ],
)
def test_fermat_scan(scan_msg, reference_scan_list):
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.devices["samx"].read_buffer = {"value": 0}
    device_manager.add_device("samy")
    device_manager.devices["samy"].read_buffer = {"value": 0}
    args = unpack_scan_args(scan_msg.content.get("parameter").get("args"))
    kwargs = scan_msg.content.get("parameter").get("kwargs")
    scan = FermatSpiralScan(
        *args, parameter=scan_msg.content.get("parameter"), device_manager=device_manager, **kwargs
    )

    def offset_mock():
        yield None

    scan._set_position_offset = offset_mock
    next(scan.prepare_positions())
    # pylint: disable=protected-access
    pos = list(scan._get_position())
    assert pytest.approx(np.vstack(np.array(pos, dtype=object)[:, 1])) == np.vstack(
        np.array(reference_scan_list, dtype=object)[:, 1]
    )


@pytest.mark.parametrize(
    "scan_msg,reference_scan_list",
    [
        (
            messages.ScanQueueMessage(
                metadata={
                    "file_suffix": None,
                    "file_directory": None,
                    "user_metadata": {},
                    "RID": "a86acd69-ea4b-4b12-acbb-3f275fc5e8e3",
                },
                scan_type="cont_line_scan",
                parameter={
                    "args": ("samx", -1, 1),
                    "kwargs": {
                        "steps": 3,
                        "exp_time": 0.1,
                        "atol": 0.1,
                        "offset": 3,
                        "relative": False,
                        "system_config": {"file_suffix": None, "file_directory": None},
                    },
                },
                queue="primary",
            ),
            [
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 0},
                    device=["samx"],
                    action="read",
                    parameter={"wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 1},
                    device=["samx"],
                    action="wait",
                    parameter={"type": "read", "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 2, "response": True},
                    device="samx",
                    action="rpc",
                    parameter={"device": "samx", "func": "read", "args": (), "kwargs": {}},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 3},
                    device=None,
                    action="open_scan",
                    parameter={
                        "scan_motors": ["samx"],
                        "readout_priority": {
                            "monitored": ["samx"],
                            "baseline": [],
                            "on_request": [],
                            "async": [],
                        },
                        "num_points": 3,
                        "positions": [[-1.0], [0.0], [1.0]],
                        "scan_name": "cont_line_scan",
                        "scan_type": "step",
                    },
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 4},
                    device=None,
                    action="stage",
                    parameter={},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "baseline", "DIID": 5},
                    device=None,
                    action="baseline_reading",
                    parameter={},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 6},
                    device="samx",
                    action="set",
                    parameter={"value": -1.0, "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 7},
                    device=None,
                    action="wait",
                    parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 8},
                    device=None,
                    action="pre_scan",
                    parameter={},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 9},
                    device="samx",
                    action="set",
                    parameter={"value": -4.0, "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 10},
                    device=None,
                    action="wait",
                    parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 11},
                    device="samx",
                    action="set",
                    parameter={"value": 1.0, "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 12, "point_id": 0},
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 13, "point_id": 0},
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "primary"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 14, "point_id": 1},
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 15, "point_id": 1},
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "primary"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 16, "point_id": 2},
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 17, "point_id": 2},
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "primary"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 18},
                    device="samx",
                    action="set",
                    parameter={"value": 0, "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 19},
                    device=None,
                    action="wait",
                    parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 20},
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 21},
                    device=None,
                    action="complete",
                    parameter={},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 22},
                    device=None,
                    action="unstage",
                    parameter={},
                ),
                messages.DeviceInstructionMessage(
                    metadata={"readout_priority": "monitored", "DIID": 23},
                    device=None,
                    action="close_scan",
                    parameter={},
                ),
            ],
        )
    ],
)
def test_cont_line_scan(scan_msg, reference_scan_list):
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.devices["samx"].read_buffer = {"value": 0}

    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = ContLineScan(
        *args, device_manager=device_manager, parameter=scan_msg.content["parameter"], **kwargs
    )

    readback = collections.deque()
    readback.extend([{"samx": {"value": -1}}, {"samx": {"value": 0}}, {"samx": {"value": 1}}])

    def mock_readback_return():
        if len(readback) > 0:
            return readback.popleft()
        return None

    with (
        mock.patch.object(request.device_manager.devices["samx"], "readback") as mock_readback,
        mock.patch.object(request.stubs, "_get_from_rpc") as mock_rpc,
    ):
        mock_readback.read.side_effect = mock_readback_return
        mock_rpc.return_value = {"samx": {"value": 0}}

        msg_list = list(request.run())

        scan_uid = msg_list[0].metadata.get("scan_id")
        for ii, msg in enumerate(msg_list):
            if msg is None:
                msg_list.pop(ii)
                continue
            if msg.metadata.get("RID") is not None:
                msg.metadata.pop("RID")
            if msg.action == "rpc":
                msg.parameter.pop("rpc_id")
        assert msg_list == reference_scan_list


def test_device_rpc():
    device_manager = DMMock()
    parameter = {
        "device": "samx",
        "rpc_id": "baf7c4c0-4948-4046-8fc5-ad1e9d188c10",
        "func": "read",
        "args": [],
        "kwargs": {},
    }

    scan = DeviceRPC(parameter=parameter, device_manager=device_manager)
    scan_instructions = list(scan.run())
    assert scan_instructions == [
        messages.DeviceInstructionMessage(
            device="samx",
            action="rpc",
            parameter=parameter,
            metadata={"readout_priority": "monitored", "DIID": 0},
        )
    ]


@pytest.mark.parametrize(
    "scan_msg,reference_scan_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="acquire",
                parameter={"args": [], "kwargs": {"exp_time": 1.0}},
                queue="primary",
            ),
            [
                messages.DeviceInstructionMessage(
                    device=None,
                    action="open_scan",
                    parameter={
                        "scan_motors": [],
                        "readout_priority": {
                            "monitored": [],
                            "baseline": [],
                            "on_request": [],
                            "async": [],
                        },
                        "num_points": 1,
                        "positions": [],
                        "scan_name": "acquire",
                        "scan_type": "step",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 0},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="stage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 1},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="baseline_reading",
                    parameter={},
                    metadata={"readout_priority": "baseline", "DIID": 2},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="pre_scan",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 3},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"point_id": 0, "readout_priority": "monitored", "DIID": 3},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "group": "trigger", "time": 1},
                    metadata={"readout_priority": "monitored", "DIID": 4},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"point_id": 0, "readout_priority": "monitored", "DIID": 5},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 6},
                ),
                messages.DeviceInstructionMessage(
                    **{"device": None, "action": "complete", "parameter": {}},
                    metadata={"readout_priority": "monitored", "DIID": 31},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="unstage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 17},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="close_scan",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 18},
                ),
            ],
        )
    ],
)
def test_acquire(scan_msg, reference_scan_list):
    device_manager = DMMock()

    scan = Acquire(exp_time=1, device_manager=device_manager)
    scan_instructions = list(scan.run())
    scan_uid = scan_instructions[0].metadata.get("scan_id")
    for ii, _ in enumerate(reference_scan_list):
        if reference_scan_list[ii].metadata.get("scan_id") is not None:
            reference_scan_list[ii].metadata["scan_id"] = scan_uid
        reference_scan_list[ii].metadata["DIID"] = ii
    assert scan_instructions == reference_scan_list


def test_pre_scan_macro():
    def pre_scan_macro(devices: dict, request: RequestBase):
        pass

    device_manager = DMMock()
    device_manager.add_device("samx")
    macros = inspect.getsource(pre_scan_macro).encode()
    scan_msg = messages.ScanQueueMessage(
        scan_type="fermat_scan",
        parameter={"args": {"samx": (-5, 5), "samy": (-5, 5)}, "kwargs": {"step": 3}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content.get("parameter", {}).get("args", []))
    kwargs = scan_msg.content.get("parameter", {}).get("kwargs", {})
    request = FermatSpiralScan(
        *args, device_manager=device_manager, parameter=scan_msg.content["parameter"], **kwargs
    )
    with mock.patch.object(
        request.device_manager.connector,
        "lrange",
        new_callable=mock.PropertyMock,
        return_value=[messages.VariableMessage(value=macros)],
    ) as macros_mock:
        with mock.patch.object(request, "_get_func_name_from_macro", return_value="pre_scan_macro"):
            with mock.patch("builtins.eval") as eval_mock:
                request.initialize()
                eval_mock.assert_called_once_with("pre_scan_macro")


# def test_scan_report_devices():
#     device_manager = DMMock()
#     device_manager.add_device("samx")
#     parameter = {
#         "args": {"samx": (-5, 5), "samy": (-5, 5)},
#         "kwargs": {"step": 3},
#     }
#     request = RequestBase(device_manager=device_manager, parameter=parameter)
#     assert request.scan_report_devices == ["samx", "samy"]
#     request.scan_report_devices = ["samx", "samz"]
#     assert request.scan_report_devices == ["samx", "samz"]


@pytest.mark.parametrize("in_args,reference_positions", [((5, 5, 1, 1), [[1, 0], [2, 0], [-2, 0]])])
def test_round_roi_scan_positions(in_args, reference_positions):
    positions = get_round_roi_scan_positions(*in_args)
    assert np.isclose(positions, reference_positions).all()


def test_round_roi_scan():
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samy")
    scan_msg = messages.ScanQueueMessage(
        scan_type="round_roi_scan",
        parameter={
            "args": {"samx": (10,), "samy": (10,)},
            "kwargs": {"dr": 2, "nth": 4, "exp_time": 2, "relative": True},
        },
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = RoundROIScan(
        *args, device_manager=device_manager, parameter=scan_msg.content["parameter"], **kwargs
    )
    assert set(request.scan_report_devices) == set(["samx", "samy"])
    assert request.dr == 2
    assert request.nth == 4
    assert request.exp_time == 2
    assert request.relative is True


@pytest.mark.parametrize(
    "in_args,reference_positions", [((1, 5, 1, 1), [[0, -3], [0, -7], [0, 7]])]
)
def test_round_scan_positions(in_args, reference_positions):
    positions = get_round_scan_positions(*in_args)
    assert np.isclose(positions, reference_positions).all()


@pytest.mark.parametrize(
    "in_args,reference_positions,snaked",
    [
        (([list(range(2)), list(range(2))],), [[0, 1], [0, 0], [1, 0], [1, 1]], True),
        (
            ([list(range(2)), list(range(3))],),
            [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2]],
            False,
        ),
    ],
)
def test_raster_scan_positions(in_args, reference_positions, snaked):
    positions = get_2D_raster_pos(*in_args, snaked=snaked)
    assert np.isclose(positions, reference_positions).all()


@pytest.mark.parametrize(
    "in_args, center, reference_positions",
    [
        (
            [-2, 2, -2, 2],
            False,
            [
                [-0.38502947, -0.42030026],
                [0.8030152, 0.07047403],
                [-0.78349739, 0.6006928],
                [0.19856742, -1.12257337],
                [0.68409143, 1.07541569],
                [-1.34834023, -0.36246191],
                [1.33834167, -0.69508386],
                [-0.55304807, 1.51437705],
                [-0.65246146, -1.5806309],
                [1.63258446, 0.76398167],
                [-1.80382449, 0.565789],
                [0.99004828, -1.70839234],
                [-1.74471832, -1.22660425],
                [-1.46933912, 1.74339971],
                [1.70582397, 1.71416585],
                [1.95717083, -1.63324289],
            ],
        ),
        (
            [-1, 1, -1, 1],
            1,
            [
                [0.0, 0.0],
                [-0.38502947, -0.42030026],
                [0.8030152, 0.07047403],
                [-0.78349739, 0.6006928],
            ],
        ),
    ],
)
def test_get_fermat_spiral_pos(in_args, center, reference_positions):
    positions = get_fermat_spiral_pos(*in_args, center=center)
    assert np.isclose(positions, reference_positions).all()


def test_get_func_name_from_macro():
    def pre_scan_macro(devices: dict, request: RequestBase):
        pass

    device_manager = DMMock()
    device_manager.add_device("samx")
    macros = [inspect.getsource(pre_scan_macro).encode()]
    scan_msg = messages.ScanQueueMessage(
        scan_type="fermat_scan",
        parameter={"args": {"samx": (-5, 5), "samy": (-5, 5)}, "kwargs": {"step": 3}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content.get("parameter", {}).get("args", []))
    kwargs = scan_msg.content.get("parameter", {}).get("kwargs", {})
    request = FermatSpiralScan(
        *args, device_manager=device_manager, parameter=scan_msg.content["parameter"], **kwargs
    )
    assert request._get_func_name_from_macro(macros[0].decode().strip()) == "pre_scan_macro"


def test_scan_report_devices():
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samy")
    scan_msg = messages.ScanQueueMessage(
        scan_type="fermat_scan",
        parameter={"args": {"samx": (-5, 5), "samy": (-5, 5)}, "kwargs": {"step": 3}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content.get("parameter", {}).get("args", []))
    kwargs = scan_msg.content.get("parameter", {}).get("kwargs", {})

    request = FermatSpiralScan(
        *args, device_manager=device_manager, parameter=scan_msg.content["parameter"], **kwargs
    )
    assert set(request.scan_report_devices) == set(["samx", "samy"])

    request.scan_report_devices = ["samx", "samy", "samz"]
    assert request.scan_report_devices == ["samx", "samy", "samz"]


def test_request_base_check_limits():
    class RequestBaseMock(RequestBase):
        def run(self):
            pass

    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samy")
    scan_msg = messages.ScanQueueMessage(
        scan_type="fermat_scan",
        parameter={"args": {"samx": (-5, 5), "samy": (-5, 5)}, "kwargs": {"step": 3}},
        queue="primary",
    )
    request = RequestBaseMock(
        device_manager=device_manager, parameter=scan_msg.content["parameter"]
    )

    assert request.scan_motors == ["samx", "samy"]
    assert request.device_manager.devices["samy"]._config["deviceConfig"].get("limits", [0, 0]) == [
        -50,
        50,
    ]
    request.device_manager.devices["samy"]._config["deviceConfig"]["limits"] = [5, -5]
    assert request.device_manager.devices["samy"]._config["deviceConfig"].get("limits", [0, 0]) == [
        5,
        -5,
    ]

    request.positions = [[-100, 30]]

    for ii, dev in enumerate(request.scan_motors):
        low_limit, high_limit = (
            request.device_manager.devices[dev]._config["deviceConfig"].get("limits", [0, 0])
        )
        for pos in request.positions:
            pos_axis = pos[ii]
            if low_limit >= high_limit:
                continue
            if not low_limit <= pos_axis <= high_limit:
                with pytest.raises(Exception) as exc_info:
                    request._check_limits()
                assert (
                    exc_info.value.args[0]
                    == f"Target position {pos} for motor {dev} is outside of range: [{low_limit},"
                    f" {high_limit}]"
                )
            else:
                request._check_limits()

    assert request.positions == [[-100, 30]]


def test_request_base_get_scan_motors():
    class RequestBaseMock(RequestBase):
        def run(self):
            pass

    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samz")
    scan_msg = messages.ScanQueueMessage(
        scan_type="fermat_scan",
        parameter={"args": {"samx": (-5, 5)}, "kwargs": {"step": 3}},
        queue="primary",
    )
    request = RequestBaseMock(
        device_manager=device_manager, parameter=scan_msg.content["parameter"]
    )

    assert request.scan_motors == ["samx"]
    request.caller_args = ""
    request._get_scan_motors()
    assert request.scan_motors == ["samx"]

    request.arg_bundle_size = {"bundle": 2, "min": None, "max": None}
    request.caller_args = {"samz": (-2, 2), "samy": (-1, 2)}
    request._get_scan_motors()
    assert request.scan_motors == ["samz", "samy"]

    request.caller_args = {"samx"}
    request.arg_bundle_size = {"bundle": 0, "min": None, "max": None}
    request._get_scan_motors()
    assert request.scan_motors == ["samz", "samy", "samx"]


def test_scan_base_init():
    device_manager = DMMock()
    device_manager.add_device("samx")

    class ScanBaseMock(ScanBase):
        scan_name = ""

        def _calculate_positions(self):
            pass

    scan_msg = messages.ScanQueueMessage(
        scan_type="",
        parameter={"args": {"samx": (-5, 5), "samy": (-5, 5)}, "kwargs": {"step": 3}},
        queue="primary",
    )
    with pytest.raises(ValueError) as exc_info:
        request = ScanBaseMock(
            device_manager=device_manager, parameter=scan_msg.content["parameter"]
        )
    assert exc_info.value.args[0] == "scan_name cannot be empty"


def test_scan_base_set_position_offset():
    device_manager = DMMock()
    device_manager.add_device("samx")
    device_manager.add_device("samy")

    scan_msg = messages.ScanQueueMessage(
        scan_type="fermat_scan",
        parameter={
            "args": {"samx": (-5, 5), "samy": (-5, 5)},
            "kwargs": {"step": 3, "relative": False},
        },
        queue="primary",
    )

    args = unpack_scan_args(scan_msg.content.get("parameter", {}).get("args", []))
    kwargs = scan_msg.content.get("parameter", {}).get("kwargs", {})
    request = FermatSpiralScan(
        *args, device_manager=device_manager, parameter=scan_msg.content["parameter"], **kwargs
    )

    assert request.positions == []
    request._set_position_offset()
    assert request.positions == []

    assert request.relative is False
    request._set_position_offset()

    assert request.start_pos == []


def test_round_scan_fly_sim_get_scan_motors():
    device_manager = DMMock()
    device_manager.add_device("flyer_sim")
    scan_msg = messages.ScanQueueMessage(
        scan_type="round_scan_fly",
        parameter={"args": {"flyer_sim": (0, 50, 5, 3)}, "kwargs": {"realtive": True}},
        queue="primary",
    )
    request = RoundScanFlySim(
        flyer="flyer_sim",
        inner_ring=0,
        outer_ring=50,
        number_of_rings=5,
        number_pos=3,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
    )

    request._get_scan_motors()
    assert request.scan_motors == []
    assert request.flyer == list(scan_msg.content["parameter"]["args"].keys())[0]


def test_round_scan_fly_sim_prepare_positions():
    device_manager = DMMock()
    device_manager.add_device("flyer_sim")
    scan_msg = messages.ScanQueueMessage(
        scan_type="round_scan_fly",
        parameter={"args": {"flyer_sim": (0, 50, 5, 3)}, "kwargs": {"realtive": True}},
        queue="primary",
    )
    request = RoundScanFlySim(
        flyer="flyer_sim",
        inner_ring=0,
        outer_ring=50,
        number_of_rings=5,
        number_pos=3,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
    )
    request._calculate_positions = mock.MagicMock()
    request._check_limits = mock.MagicMock()
    pos = [1, 2, 3, 4]
    request.positions = pos

    next(request.prepare_positions())

    request._calculate_positions.assert_called_once()
    assert request.num_pos == len(pos)
    request._check_limits.assert_called_once()


@pytest.mark.parametrize(
    "in_args,reference_positions", [((1, 5, 1, 1), [[0, -3], [0, -7], [0, 7]])]
)
def test_round_scan_fly_sim_calculate_positions(in_args, reference_positions):
    device_manager = DMMock()
    device_manager.add_device("flyer_sim")
    scan_msg = messages.ScanQueueMessage(
        scan_type="round_scan_fly",
        parameter={"args": {"flyer_sim": in_args}, "kwargs": {"realtive": True}},
        queue="primary",
    )
    request = RoundScanFlySim(
        flyer="flyer_sim",
        inner_ring=in_args[0],
        outer_ring=in_args[1],
        number_of_rings=in_args[2],
        number_pos=in_args[3],
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
    )

    request._calculate_positions()
    assert np.isclose(request.positions, reference_positions).all()


@pytest.mark.parametrize(
    "in_args,reference_positions", [((1, 5, 1, 1), [[0, -3], [0, -7], [0, 7]])]
)
def test_round_scan_fly_sim_scan_core(in_args, reference_positions):
    device_manager = DMMock()
    device_manager.add_device("flyer_sim")
    scan_msg = messages.ScanQueueMessage(
        scan_type="round_scan_fly",
        parameter={"args": {"flyer_sim": in_args}, "kwargs": {"realtive": True}},
        queue="primary",
    )
    request = RoundScanFlySim(
        flyer="flyer_sim",
        inner_ring=in_args[0],
        outer_ring=in_args[1],
        number_of_rings=in_args[2],
        number_pos=in_args[3],
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
    )
    request.positions = np.array(reference_positions)

    ret = next(request.scan_core())
    assert ret == messages.DeviceInstructionMessage(
        device="flyer_sim",
        action="kickoff",
        parameter={
            "configure": {"num_pos": 0, "positions": reference_positions, "exp_time": 0},
            "wait_group": "kickoff",
        },
        metadata={"readout_priority": "monitored", "DIID": 0},
    )


@pytest.mark.parametrize(
    "in_args,reference_positions",
    [
        (
            [[-3, 3], [-2, 2]],
            [
                [-3.0, -2.0],
                [-2.33333333, -1.55555556],
                [-1.66666667, -1.11111111],
                [-1.0, -0.66666667],
                [-0.33333333, -0.22222222],
                [0.33333333, 0.22222222],
                [1.0, 0.66666667],
                [1.66666667, 1.11111111],
                [2.33333333, 1.55555556],
                [3.0, 2.0],
            ],
        ),
        (
            [[-1, 1], [-1, 2]],
            [
                [-1.0, -1.0],
                [-0.77777778, -0.66666667],
                [-0.55555556, -0.33333333],
                [-0.33333333, 0.0],
                [-0.11111111, 0.33333333],
                [0.11111111, 0.66666667],
                [0.33333333, 1.0],
                [0.55555556, 1.33333333],
                [0.77777778, 1.66666667],
                [1.0, 2.0],
            ],
        ),
    ],
)
def test_line_scan_calculate_positions(in_args, reference_positions):
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="line_scan",
        parameter={
            "args": {"samx": in_args[0], "samy": in_args[1]},
            "kwargs": {"relative": True, "steps": 10},
        },
        queue="primary",
    )
    request = LineScan(
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )

    request._calculate_positions()
    assert np.isclose(request.positions, reference_positions).all()


def test_list_scan_calculate_positions():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="list_scan",
        parameter={
            "args": {"samx": [[0, 1, 2, 3, 4]], "samy": [[0, 1, 2, 3, 4]]},
            "kwargs": {"realtive": True},
        },
        queue="primary",
    )

    request = ListScan(device_manager=device_manager, parameter=scan_msg.content["parameter"])
    request._calculate_positions()
    assert np.isclose(request.positions, [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]]).all()


def test_list_scan_raises_for_different_lengths():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="list_scan",
        parameter={
            "args": {"samx": [[0, 1, 2, 3, 4]], "samy": [[0, 1, 2, 3]]},
            "kwargs": {"realtive": True},
        },
        queue="primary",
    )
    with pytest.raises(ValueError):
        ListScan(device_manager=device_manager, parameter=scan_msg.content["parameter"])


@pytest.mark.parametrize(
    "scan_msg,reference_scan_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="time_scan",
                parameter={
                    "args": {},
                    "kwargs": {"points": 3, "interval": 1, "exp_time": 0.1, "relative": True},
                },
                queue="primary",
            ),
            [
                messages.DeviceInstructionMessage(
                    device=[],
                    action="read",
                    parameter={"wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 0},
                ),
                messages.DeviceInstructionMessage(
                    device=[],
                    action="wait",
                    parameter={"type": "read", "wait_group": "scan_motor"},
                    metadata={"readout_priority": "monitored", "DIID": 1},
                ),
                None,
                None,
                messages.DeviceInstructionMessage(
                    device=None,
                    action="open_scan",
                    parameter={
                        "scan_motors": [],
                        "readout_priority": {
                            "monitored": [],
                            "baseline": [],
                            "on_request": [],
                            "async": [],
                        },
                        "num_points": 3,
                        "positions": [],
                        "scan_name": "time_scan",
                        "scan_type": "step",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 2},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="stage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 3},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="baseline_reading",
                    parameter={},
                    metadata={"readout_priority": "baseline", "DIID": 4},
                ),
                messages.DeviceInstructionMessage(
                    **{"device": None, "action": "pre_scan", "parameter": {}},
                    metadata={"readout_priority": "monitored", "DIID": 5},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 6, "point_id": 0},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "time": 0.1, "group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 7},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 8, "point_id": 0},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "time": 0.9, "group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 9},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 10},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 11, "point_id": 1},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "time": 0.1, "group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 12},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 13, "point_id": 1},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "time": 0.9, "group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 14},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 15},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="trigger",
                    parameter={"group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 16, "point_id": 2},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "time": 0.1, "group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 17},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 18, "point_id": 2},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "trigger", "time": 0.9, "group": "trigger"},
                    metadata={"readout_priority": "monitored", "DIID": 19},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 20},
                ),
                messages.DeviceInstructionMessage(
                    **{"device": None, "action": "complete", "parameter": {}},
                    metadata={"readout_priority": "monitored", "DIID": 21},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="unstage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 22},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="close_scan",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 23},
                ),
            ],
        )
    ],
)
def test_time_scan(scan_msg, reference_scan_list):
    device_manager = DMMock()
    request = TimeScan(
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )
    scan_instructions = list(request.run())
    assert scan_instructions == reference_scan_list


@pytest.mark.parametrize(
    "scan_msg,reference_scan_list",
    [
        (
            messages.ScanQueueMessage(
                scan_type="otf_scan",
                parameter={"args": {}, "kwargs": {"e1": 700, "e2": 740, "time": 4}},
                queue="primary",
                metadata={"RID": "1234"},
            ),
            [
                None,
                None,
                None,
                messages.DeviceInstructionMessage(
                    device=None,
                    action="open_scan",
                    parameter={
                        "scan_motors": [],
                        "readout_priority": {
                            "monitored": [],
                            "baseline": [],
                            "on_request": [],
                            "async": [],
                        },
                        "num_points": 0,
                        "positions": [],
                        "scan_name": "otf_scan",
                        "scan_type": "fly",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 0, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="stage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 1, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="baseline_reading",
                    parameter={},
                    metadata={"readout_priority": "baseline", "DIID": 2, "RID": "1234"},
                ),
                None,
                messages.DeviceInstructionMessage(
                    device="mono",
                    action="set",
                    parameter={"value": 700, "wait_group": "flyer"},
                    metadata={"readout_priority": "monitored", "DIID": 3, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=["mono"],
                    action="wait",
                    parameter={"type": "move", "wait_group": "flyer"},
                    metadata={"readout_priority": "monitored", "DIID": 4, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device="otf",
                    action="kickoff",
                    parameter={
                        "configure": {"e1": 700, "e2": 740, "time": 4},
                        "wait_group": "kickoff",
                    },
                    metadata={"readout_priority": "monitored", "DIID": 5, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=["otf"],
                    action="wait",
                    parameter={"type": "move", "wait_group": "kickoff"},
                    metadata={"readout_priority": "monitored", "DIID": 6, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device="otf",
                    action="complete",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 7, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="read",
                    parameter={"group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 8, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 9, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="wait",
                    parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
                    metadata={"readout_priority": "monitored", "DIID": 10, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    **{"device": None, "action": "complete", "parameter": {}},
                    metadata={"readout_priority": "monitored", "DIID": 11, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="unstage",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 12, "RID": "1234"},
                ),
                messages.DeviceInstructionMessage(
                    device=None,
                    action="close_scan",
                    parameter={},
                    metadata={"readout_priority": "monitored", "DIID": 13, "RID": "1234"},
                ),
            ],
        )
    ],
)
def test_otf_scan(scan_msg, reference_scan_list):
    device_manager = DMMock()
    request = OTFScan(
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        metadata=scan_msg.metadata,
    )
    with mock.patch.object(request.stubs, "get_req_status", return_value=1):
        scan_instructions = list(request.run())
    assert scan_instructions == reference_scan_list


def test_monitor_scan():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="monitor_scan",
        parameter={"args": {"samx": [-5, 5]}, "kwargs": {"relative": True, "exp_time": 0.1}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = MonitorScan(
        *args,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )
    request._calculate_positions()
    assert np.isclose(request.positions, [[-5], [5]]).all()


def test_monitor_scan_run():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="monitor_scan",
        parameter={"args": {"samx": [-5, 5]}, "kwargs": {"relative": True, "exp_time": 0.1}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = MonitorScan(
        *args,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )
    with mock.patch.object(request, "_get_flyer_status") as flyer_status:
        with mock.patch.object(request, "_check_limits") as check_limits:
            with mock.patch.object(request, "_set_position_offset") as position_offset:
                flyer_status.side_effect = [
                    (None, None),
                    (None, None),
                    (None, messages.DeviceMessage(signals={"rb1": {"value": 1}})),
                    (True, None),
                ]
                ref_list = list(request.run())
                assert ref_list == [
                    messages.DeviceInstructionMessage(
                        device=["samx"],
                        action="read",
                        parameter={"wait_group": "scan_motor"},
                        metadata={"readout_priority": "monitored", "DIID": 0},
                    ),
                    messages.DeviceInstructionMessage(
                        device=["samx"],
                        action="wait",
                        parameter={"type": "read", "wait_group": "scan_motor"},
                        metadata={"readout_priority": "monitored", "DIID": 1},
                    ),
                    None,
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="open_scan",
                        parameter={
                            "scan_motors": ["samx"],
                            "readout_priority": {
                                "monitored": ["samx"],
                                "baseline": [],
                                "on_request": [],
                                "async": [],
                            },
                            "num_points": 0,
                            "positions": [[-5.0], [5.0]],
                            "scan_name": "monitor_scan",
                            "scan_type": "fly",
                        },
                        metadata={"readout_priority": "monitored", "DIID": 2},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="stage",
                        parameter={},
                        metadata={"readout_priority": "monitored", "DIID": 3},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="baseline_reading",
                        parameter={},
                        metadata={"readout_priority": "baseline", "DIID": 4},
                    ),
                    messages.DeviceInstructionMessage(
                        device="samx",
                        action="set",
                        parameter={"value": -5.0, "wait_group": "scan_motor"},
                        metadata={"readout_priority": "monitored", "DIID": 5},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="wait",
                        parameter={
                            "type": "move",
                            "group": "scan_motor",
                            "wait_group": "scan_motor",
                        },
                        metadata={"readout_priority": "monitored", "DIID": 6},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="pre_scan",
                        parameter={},
                        metadata={"readout_priority": "monitored", "DIID": 7},
                    ),
                    messages.DeviceInstructionMessage(
                        device="samx",
                        action="set",
                        parameter={"value": -5.0, "wait_group": "scan_motor"},
                        metadata={"readout_priority": "monitored", "DIID": 8},
                    ),
                    messages.DeviceInstructionMessage(
                        device="samx",
                        action="wait",
                        parameter={"type": "move", "wait_group": "scan_motor"},
                        metadata={"readout_priority": "monitored", "DIID": 9},
                    ),
                    messages.DeviceInstructionMessage(
                        device="samx",
                        action="set",
                        parameter={"value": 5.0, "wait_group": "scan_motor"},
                        metadata={"readout_priority": "monitored", "DIID": 10, "response": True},
                    ),
                    messages.DeviceInstructionMessage(
                        device="samx",
                        action="publish_data_as_read",
                        parameter={"data": {"rb1": {"value": 1}}},
                        metadata={"readout_priority": "monitored", "DIID": 11, "point_id": 0},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="wait",
                        parameter={
                            "type": "read",
                            "group": "primary",
                            "wait_group": "readout_primary",
                        },
                        metadata={"readout_priority": "monitored", "DIID": 12},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="complete",
                        parameter={},
                        metadata={"readout_priority": "monitored", "DIID": 13},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="unstage",
                        parameter={},
                        metadata={"readout_priority": "monitored", "DIID": 14},
                    ),
                    messages.DeviceInstructionMessage(
                        device=None,
                        action="close_scan",
                        parameter={},
                        metadata={"readout_priority": "monitored", "DIID": 15},
                    ),
                ]


def test_OpenInteractiveScan():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="open_interactive_scan",
        parameter={"args": {"samx": []}, "kwargs": {"relative": True, "exp_time": 0.1}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = OpenInteractiveScan(
        *args,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )
    ref_list = list(request.run())
    assert ref_list == [
        messages.DeviceInstructionMessage(
            device=None,
            action="open_scan_def",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 0},
        ),
        messages.DeviceInstructionMessage(
            device=["samx"],
            action="read",
            parameter={"wait_group": "scan_motor"},
            metadata={"readout_priority": "monitored", "DIID": 1},
        ),
        messages.DeviceInstructionMessage(
            device=["samx"],
            action="wait",
            parameter={"type": "read", "wait_group": "scan_motor"},
            metadata={"readout_priority": "monitored", "DIID": 2},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="open_scan",
            parameter={
                "scan_motors": ["samx"],
                "readout_priority": {
                    "monitored": ["samx"],
                    "baseline": [],
                    "on_request": [],
                    "async": [],
                },
                "num_points": 0,
                "positions": [],
                "scan_name": "open_interactive_scan",
                "scan_type": "step",
            },
            metadata={"readout_priority": "monitored", "DIID": 3},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="stage",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 4},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="baseline_reading",
            parameter={},
            metadata={"readout_priority": "baseline", "DIID": 5},
        ),
    ]


def test_AddInteractiveScanPointn():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="interactive_scan_trigger",
        parameter={"args": {"samx": []}, "kwargs": {"relative": True, "exp_time": 0.1}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = AddInteractiveScanPoint(
        *args,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )
    ref_list = list(request.run())
    assert ref_list == [
        messages.DeviceInstructionMessage(
            device=None,
            action="open_scan",
            parameter={
                "scan_motors": ["samx"],
                "readout_priority": {
                    "monitored": ["samx"],
                    "baseline": [],
                    "on_request": [],
                    "async": [],
                },
                "num_points": 0,
                "positions": [],
                "scan_name": "interactive_scan_trigger",
                "scan_type": "step",
            },
            metadata={"readout_priority": "monitored", "DIID": 0},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="trigger",
            parameter={"group": "trigger"},
            metadata={"readout_priority": "monitored", "DIID": 1, "point_id": 0},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="wait",
            parameter={"type": "trigger", "time": 0.1, "group": "trigger"},
            metadata={"readout_priority": "monitored", "DIID": 2},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="read",
            parameter={"group": "primary", "wait_group": "readout_primary"},
            metadata={"readout_priority": "monitored", "DIID": 3, "point_id": 0},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="wait",
            parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
            metadata={"readout_priority": "monitored", "DIID": 4},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="close_scan",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 5},
        ),
    ]


def test_CloseInteractiveScan():
    device_manager = DMMock()
    device_manager.add_device("samx")
    scan_msg = messages.ScanQueueMessage(
        scan_type="close_interactive_scan",
        parameter={"args": {"samx": []}, "kwargs": {"relative": True, "exp_time": 0.1}},
        queue="primary",
    )
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    kwargs = scan_msg.content["parameter"]["kwargs"]
    request = CloseInteractiveScan(
        *args,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )
    request.start_pos = [0]
    ref_list = list(request.run())
    assert ref_list == [
        messages.DeviceInstructionMessage(
            device="samx",
            action="set",
            parameter={"value": 0, "wait_group": "scan_motor"},
            metadata={"readout_priority": "monitored", "DIID": 0},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="wait",
            parameter={"type": "move", "group": "scan_motor", "wait_group": "scan_motor"},
            metadata={"readout_priority": "monitored", "DIID": 1},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="wait",
            parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
            metadata={"readout_priority": "monitored", "DIID": 2},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="complete",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 3},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="unstage",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 4},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="close_scan",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 5},
        ),
        messages.DeviceInstructionMessage(
            device=None,
            action="close_scan_def",
            parameter={},
            metadata={"readout_priority": "monitored", "DIID": 6},
        ),
    ]


def test_RoundScan():
    device_manager = DMMock()
    scan_msg = messages.ScanQueueMessage(
        scan_type="round_scan",
        parameter={
            "args": {"samx": ["samy", 1, 2, 1, 3]},
            "kwargs": {"relative": True, "steps": 10},
        },
        queue="primary",
    )
    #     "motor_1": ScanArgType.DEVICE,
    # "motor_2": ScanArgType.DEVICE,
    # "inner_ring": ScanArgType.FLOAT,
    # "outer_ring": ScanArgType.FLOAT,
    # "number_of_rings": ScanArgType.INT,
    # "number_of_positions_in_first_ring": ScanArgType.INT,
    args = unpack_scan_args(scan_msg.content["parameter"]["args"])
    request = RoundScan(
        *args,
        device_manager=device_manager,
        parameter=scan_msg.content["parameter"],
        **scan_msg.content["parameter"]["kwargs"],
    )

    with mock.patch.object(request, "_check_limits") as check_limits:
        with mock.patch.object(request, "_set_position_offset") as position_offset:
            ref = list(request.run())
            assert len(ref) == 85


def test_ContLineFlyScan():
    device_manager = DMMock()
    device_manager.add_device("samx")
    request = ContLineFlyScan(
        motor="samx", start=0, stop=5, relative=False, device_manager=device_manager
    )
    with mock.patch.object(request.stubs, "request_is_completed") as req_completed:
        req_completed.side_effect = [False, True]
        ref_list = list(request.run())
        assert len(req_completed.mock_calls) == 2
    ref_list[1].parameter["readback"]["RID"] = "ddaad496-6178-4f6a-8c2e-0c9d416e5d9c"
    for item in ref_list:
        if hasattr(item, "metadata") and "RID" in item.metadata:
            item.metadata["RID"] = "ddaad496-6178-4f6a-8c2e-0c9d416e5d9c"

    assert ref_list == [
        None,
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 0},
            device=None,
            action="scan_report_instruction",
            parameter={
                "readback": {
                    "RID": "ddaad496-6178-4f6a-8c2e-0c9d416e5d9c",
                    "devices": ["samx"],
                    "start": [0],
                    "end": np.array([5]),
                }
            },
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 1},
            device=None,
            action="open_scan",
            parameter={
                "scan_motors": [],
                "readout_priority": {
                    "monitored": [],
                    "baseline": [],
                    "on_request": [],
                    "async": [],
                },
                "num_points": None,
                "positions": [[0], [5]],
                "scan_name": "cont_line_fly_scan",
                "scan_type": "fly",
            },
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 2},
            device=None,
            action="stage",
            parameter={},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "baseline", "DIID": 3},
            device=None,
            action="baseline_reading",
            parameter={},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 4},
            device=None,
            action="pre_scan",
            parameter={},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 5},
            device="samx",
            action="set",
            parameter={"value": 0, "wait_group": "scan_motor"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 6},
            device=["samx"],
            action="wait",
            parameter={"type": "move", "wait_group": "scan_motor"},
        ),
        messages.DeviceInstructionMessage(
            metadata={
                "readout_priority": "monitored",
                "DIID": 7,
                "response": True,
                "RID": "ddaad496-6178-4f6a-8c2e-0c9d416e5d9c",
            },
            device="samx",
            action="set",
            parameter={"value": 5, "wait_group": "set"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 8, "point_id": 0},
            device=None,
            action="trigger",
            parameter={"group": "trigger"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 9, "point_id": 0},
            device=None,
            action="read",
            parameter={"group": "primary", "wait_group": "readout_primary"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 10},
            device=None,
            action="wait",
            parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 11},
            device=None,
            action="wait",
            parameter={"type": "trigger", "time": 0, "group": "trigger"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 12, "point_id": 1},
            device=None,
            action="trigger",
            parameter={"group": "trigger"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 13, "point_id": 1},
            device=None,
            action="read",
            parameter={"group": "primary", "wait_group": "readout_primary"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 14},
            device=None,
            action="wait",
            parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 15},
            device=None,
            action="wait",
            parameter={"type": "trigger", "time": 0, "group": "trigger"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 16},
            device=None,
            action="wait",
            parameter={"type": "read", "group": "primary", "wait_group": "readout_primary"},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 17},
            device=None,
            action="complete",
            parameter={},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 18},
            device=None,
            action="unstage",
            parameter={},
        ),
        messages.DeviceInstructionMessage(
            metadata={"readout_priority": "monitored", "DIID": 19},
            device=None,
            action="close_scan",
            parameter={},
        ),
    ]
