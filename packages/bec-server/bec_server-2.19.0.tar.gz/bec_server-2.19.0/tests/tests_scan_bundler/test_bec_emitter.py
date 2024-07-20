from unittest import mock

import pytest

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_server.scan_bundler.bec_emitter import BECEmitter


@pytest.fixture
def bec_emitter_mock(scan_bundler_mock):
    emitter = BECEmitter(scan_bundler_mock)
    yield emitter
    emitter.shutdown()


def test_on_scan_point_emit_BEC(bec_emitter_mock):
    sb = bec_emitter_mock.scan_bundler
    with mock.patch.object(bec_emitter_mock, "_send_bec_scan_point") as send:
        bec_emitter_mock.on_scan_point_emit("scan_id", 2)
        send.assert_called_once_with("scan_id", 2)


def test_on_baseline_emit_BEC(bec_emitter_mock):
    sb = bec_emitter_mock.scan_bundler
    with mock.patch.object(bec_emitter_mock, "_send_baseline") as send:
        bec_emitter_mock.on_baseline_emit("scan_id")
        send.assert_called_once_with("scan_id")


def test_send_bec_scan_point(bec_emitter_mock):
    sb = bec_emitter_mock.scan_bundler
    scan_id = "lkajsdlkj"
    point_id = 2
    sb.sync_storage[scan_id] = {"info": {}, "status": "open", "sent": set()}
    sb.sync_storage[scan_id][point_id] = {}
    msg = messages.ScanMessage(
        point_id=point_id,
        scan_id=scan_id,
        data=sb.sync_storage[scan_id][point_id],
        metadata={"scan_id": "lkajsdlkj", "scan_type": None, "scan_report_devices": None},
    )
    with mock.patch.object(bec_emitter_mock, "add_message") as send:
        bec_emitter_mock._send_bec_scan_point(scan_id, point_id)
        send.assert_called_once_with(
            msg,
            MessageEndpoints.scan_segment(),
            MessageEndpoints.public_scan_segment(scan_id, point_id),
        )


def test_send_baseline_BEC(bec_emitter_mock):
    sb = bec_emitter_mock.scan_bundler
    scan_id = "lkajsdlkj"
    sb.sync_storage[scan_id] = {"info": {}, "status": "open", "sent": set()}
    sb.sync_storage[scan_id]["baseline"] = {}
    msg = messages.ScanBaselineMessage(scan_id=scan_id, data=sb.sync_storage[scan_id]["baseline"])
    with mock.patch.object(sb, "connector") as connector:
        bec_emitter_mock._send_baseline(scan_id)
        pipe = connector.pipeline()
        connector.set.assert_called_once_with(
            MessageEndpoints.public_scan_baseline(scan_id), msg, expire=1800, pipe=pipe
        )
        connector.set_and_publish.assert_called_once_with(
            MessageEndpoints.scan_baseline(), msg, pipe=pipe
        )
