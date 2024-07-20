from unittest import mock

import pytest

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_server.scan_server.device_validation import DeviceValidation
from bec_server.scan_server.errors import ScanAbortion


@pytest.fixture
def validator():
    connector = mock.MagicMock()
    worker = mock.MagicMock()
    yield DeviceValidation(connector, worker)


def test_device_validator_devices_are_ready(validator):
    with mock.patch.object(validator, "get_device_status") as mock_get_device_status:
        mock_get_device_status.return_value = [
            messages.DeviceReqStatusMessage(
                device="dev1",
                success=True,
                metadata={"action": "complete", "scan_id": "scan_id", "RID": "RID", "DIID": 20},
            )
        ]
        assert validator.devices_are_ready(
            devices=["dev1"],
            endpoint=MessageEndpoints.device_req_status,
            message_cls=messages.DeviceReqStatusMessage,
            metadata={"scan_id": "scan_id", "RID": "RID", "DIID": 20},
            checks=[validator.devices_returned_successfully],
        )


def test_device_validator_wait_until_ready(validator):
    round_1 = [
        messages.DeviceReqStatusMessage(
            device="dev1",
            success=True,
            metadata={"action": "complete", "scan_id": "old_scan_id", "RID": "old_RID", "DIID": 20},
        )
    ]
    round_2 = [
        messages.DeviceReqStatusMessage(
            device="dev1",
            success=True,
            metadata={"action": "complete", "scan_id": "scan_id", "RID": "RID", "DIID": 20},
        )
    ]
    with mock.patch.object(validator, "get_device_status") as mock_get_device_status:
        mock_get_device_status.side_effect = [round_1, round_2]

        assert (
            validator.devices_are_ready(
                devices=["dev1"],
                endpoint=MessageEndpoints.device_req_status,
                message_cls=messages.DeviceReqStatusMessage,
                metadata={"scan_id": "scan_id", "RID": "RID", "DIID": 20},
                checks=[validator.devices_returned_successfully],
            )
            is False
        )

        assert (
            validator.devices_are_ready(
                devices=["dev1"],
                endpoint=MessageEndpoints.device_req_status,
                message_cls=messages.DeviceReqStatusMessage,
                metadata={"scan_id": "scan_id", "RID": "RID", "DIID": 20},
                checks=[validator.devices_returned_successfully],
            )
            is True
        )


def test_device_validator_raises_on_failed_status(validator):
    round_1 = [
        messages.DeviceReqStatusMessage(
            device="dev1",
            success=True,
            metadata={"action": "complete", "scan_id": "old_scan_id", "RID": "old_RID", "DIID": 20},
        )
    ]
    round_2 = [
        messages.DeviceReqStatusMessage(
            device="dev1",
            success=False,
            metadata={"action": "complete", "scan_id": "scan_id", "RID": "RID", "DIID": 20},
        )
    ]
    with mock.patch.object(validator, "get_device_status") as mock_get_device_status:
        mock_get_device_status.side_effect = [round_1, round_2]

        assert (
            validator.devices_are_ready(
                devices=["dev1"],
                endpoint=MessageEndpoints.device_req_status,
                message_cls=messages.DeviceReqStatusMessage,
                metadata={"scan_id": "scan_id", "RID": "RID", "DIID": 20},
                checks=[validator.devices_returned_successfully],
            )
            is False
        )
        with pytest.raises(ScanAbortion):
            validator.devices_are_ready(
                devices=["dev1"],
                endpoint=MessageEndpoints.device_req_status,
                message_cls=messages.DeviceReqStatusMessage,
                metadata={"scan_id": "scan_id", "RID": "RID", "DIID": 20},
                checks=[validator.devices_returned_successfully],
            )
