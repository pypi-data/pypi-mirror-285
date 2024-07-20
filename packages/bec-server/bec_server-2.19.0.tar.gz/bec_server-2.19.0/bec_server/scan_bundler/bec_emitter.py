from __future__ import annotations

from typing import TYPE_CHECKING

from bec_lib import messages
from bec_lib.endpoints import MessageEndpoints
from bec_lib.logger import bec_logger

from .emitter import EmitterBase

logger = bec_logger.logger

if TYPE_CHECKING:
    from .scan_bundler import ScanBundler


class BECEmitter(EmitterBase):
    def __init__(self, scan_bundler: ScanBundler) -> None:
        super().__init__(scan_bundler.connector)
        self.scan_bundler = scan_bundler

    def on_scan_point_emit(self, scan_id: str, point_id: int):
        self._send_bec_scan_point(scan_id, point_id)

    def on_baseline_emit(self, scan_id: str):
        self._send_baseline(scan_id)

    def _send_bec_scan_point(self, scan_id: str, point_id: int) -> None:
        sb = self.scan_bundler

        info = sb.sync_storage[scan_id]["info"]
        msg = messages.ScanMessage(
            point_id=point_id,
            scan_id=scan_id,
            data=sb.sync_storage[scan_id][point_id],
            metadata={
                "scan_id": scan_id,
                "scan_type": info.get("scan_type"),
                "scan_report_devices": info.get("scan_report_devices"),
            },
        )
        self.add_message(
            msg,
            MessageEndpoints.scan_segment(),
            MessageEndpoints.public_scan_segment(scan_id=scan_id, point_id=point_id),
        )
        self._update_scan_progress(scan_id, point_id)

    def _update_scan_progress(self, scan_id: str, point_id: int, done=False) -> None:
        info = self.scan_bundler.sync_storage[scan_id]["info"]
        msg = messages.ProgressMessage(
            value=point_id + 1,
            max_value=info.get("num_points", point_id + 1),
            done=done,
            metadata={
                "scan_id": scan_id,
                "RID": info.get("RID", ""),
                "queue_id": info.get("queue_id", ""),
            },
        )
        self.scan_bundler.connector.set_and_publish(MessageEndpoints.scan_progress(), msg)

    def _send_baseline(self, scan_id: str) -> None:
        sb = self.scan_bundler

        msg = messages.ScanBaselineMessage(
            scan_id=scan_id,
            data=sb.sync_storage[scan_id]["baseline"],
            metadata=sb.sync_storage[scan_id]["info"],
        )
        pipe = sb.connector.pipeline()
        sb.connector.set(
            MessageEndpoints.public_scan_baseline(scan_id=scan_id), msg, expire=1800, pipe=pipe
        )
        sb.connector.set_and_publish(MessageEndpoints.scan_baseline(), msg, pipe=pipe)
        pipe.execute()

    def on_scan_status_update(self, status_msg: messages.ScanStatusMessage):
        if status_msg.status == "open":
            return
        num_points = status_msg.info.get("num_points", 0) - 1
        self._update_scan_progress(status_msg.scan_id, num_points, done=True)
