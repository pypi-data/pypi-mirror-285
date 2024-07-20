from unittest import mock

import pytest

from bec_lib import messages
from bec_server.scan_bundler.emitter import EmitterBase


@pytest.mark.parametrize(
    "msgs",
    [
        ([]),
        (
            [
                (
                    messages.ScanMessage(point_id=1, scan_id="scan_id", data={}, metadata={}),
                    "endpoint",
                    None,
                )
            ]
        ),
        (
            [
                (
                    messages.ScanMessage(point_id=1, scan_id="scan_id", data={}, metadata={}),
                    "endpoint",
                    None,
                ),
                (
                    messages.ScanMessage(point_id=2, scan_id="scan_id", data={}, metadata={}),
                    "endpoint",
                    None,
                ),
            ]
        ),
        (
            [
                (
                    messages.ScanMessage(point_id=1, scan_id="scan_id", data={}, metadata={}),
                    "endpoint",
                    "public_endpoint",
                ),
                (
                    messages.ScanMessage(point_id=2, scan_id="scan_id", data={}, metadata={}),
                    "endpoint",
                    "public_endpoint",
                ),
            ]
        ),
    ],
)
def test_publish_data(msgs):
    connector = mock.MagicMock()
    with mock.patch.object(EmitterBase, "_start_buffered_connector") as start:
        emitter = EmitterBase(connector)
        start.assert_called_once()
        with mock.patch.object(emitter, "_get_messages_from_buffer", return_value=msgs) as get_msgs:
            emitter._publish_data()
            get_msgs.assert_called_once()

            if not msgs:
                connector.send.assert_not_called()
                return

            pipe = connector.pipeline()
            msgs_bundle = messages.BundleMessage()
            _, endpoint, _ = msgs[0]
            for msg, endpoint, public in msgs:
                msg_dump = msg
                msgs_bundle.append(msg_dump)
                if public:
                    connector.set.assert_has_calls(
                        connector.set(public, msg_dump, pipe=pipe, expire=1800)
                    )

            connector.send.assert_called_with(endpoint, msgs_bundle, pipe=pipe)
        emitter.shutdown()


@pytest.mark.parametrize(
    "msg,endpoint,public",
    [
        (
            messages.ScanMessage(point_id=1, scan_id="scan_id", data={}, metadata={}),
            "endpoint",
            None,
        ),
        (
            messages.ScanMessage(point_id=1, scan_id="scan_id", data={}, metadata={}),
            "endpoint",
            "public",
        ),
    ],
)
def test_add_message(msg, endpoint, public):
    connector = mock.MagicMock()
    emitter = EmitterBase(connector)
    emitter.add_message(msg, endpoint, public)
    msgs = emitter._get_messages_from_buffer()
    out_msg, out_endpoint, out_public = msgs[0]
    assert out_msg == msg
    assert out_endpoint == endpoint
    assert out_public == public
    emitter.shutdown()
