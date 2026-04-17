from __future__ import annotations

import hashlib
from typing import Any

import pytest

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.apis import smartsheet_upload as smartsheet_upload_module
from wecom_doc_sdk.apis.smartsheet_upload import SmartSheetUploadHelper
from wecom_doc_sdk.models.uploads import (
    FinishFileUploadResponse,
    InitFileUploadRequest,
    InitFileUploadResponse,
    UploadFilePartResponse,
    UploadFileRequest,
    UploadFileResponse,
)


def test_split_file_bytes_respects_chunk_size() -> None:
    """文件切片应严格按传入 chunk_size 分块。"""

    chunks = SmartSheetUploadHelper.split_file_bytes(b"abcdefg", chunk_size=3)

    assert chunks == [b"abc", b"def", b"g"]


def test_calculate_block_sha_returns_intermediate_and_final_digest() -> None:
    """分块 sha 应包含中间 state 与最终 digest。"""

    first_chunk = b"a" * 64
    second_chunk = b"xyz"

    accumulator = smartsheet_upload_module._SHA1Accumulator()
    accumulator.update(first_chunk)
    expected_first_block_sha = accumulator.state_hexdigest()

    block_sha = SmartSheetUploadHelper.calculate_block_sha([first_chunk, second_chunk])

    assert block_sha == [
        expected_first_block_sha,
        hashlib.sha1(first_chunk + second_chunk).hexdigest(),
    ]


def test_upload_file_bytes_uses_simple_upload_path(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """小文件上传应直接走 upload_file。"""

    helper = SmartSheetUploadHelper(client)

    def fake_upload_file(
        request: UploadFileRequest | dict[str, Any],
    ) -> UploadFileResponse:
        payload = (
            client.dump_model(request)
            if isinstance(request, UploadFileRequest)
            else request
        )
        assert payload == {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "report.txt",
            "file_base64_content": "aGVsbG8=",
        }
        return UploadFileResponse(fileid="FILEID")

    monkeypatch.setattr(client.uploads, "upload_file", fake_upload_file)

    file_id = helper.upload_file_bytes(
        file_name="report.txt",
        file_bytes=b"hello",
        spaceid="SPACEID",
        fatherid="FOLDERID",
    )

    assert file_id == "FILEID"


def test_upload_file_bytes_supports_chunk_upload_path(
    client: WeComClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """大文件上传应走 init/part/finish 路径。"""

    helper = SmartSheetUploadHelper(client)
    part_calls: list[dict[str, str | int]] = []

    def fake_init_file_upload(
        request: InitFileUploadRequest | dict[str, Any],
    ) -> InitFileUploadResponse:
        payload = (
            client.dump_model(request)
            if isinstance(request, InitFileUploadRequest)
            else request
        )
        assert payload["file_name"] == "archive.bin"
        assert payload["size"] == 131
        assert len(payload["block_sha"]) == 3
        return InitFileUploadResponse(hit_exist=False, upload_key="UPLOAD_KEY")

    def fake_upload_file_part(
        request: dict[str, str | int],
    ) -> UploadFilePartResponse:
        part_calls.append(request)
        return UploadFilePartResponse()

    def fake_finish_file_upload(
        request: dict[str, object],
    ) -> FinishFileUploadResponse:
        assert request == {"upload_key": "UPLOAD_KEY"}
        return FinishFileUploadResponse(fileid="FILEID")

    monkeypatch.setattr(client.uploads, "init_file_upload", fake_init_file_upload)
    monkeypatch.setattr(client.uploads, "upload_file_part", fake_upload_file_part)
    monkeypatch.setattr(client.uploads, "finish_file_upload", fake_finish_file_upload)

    file_id = helper.upload_file_bytes(
        file_name="archive.bin",
        file_bytes=b"a" * 64 + b"b" * 64 + b"xyz",
        selected_ticket="TICKET",
        simple_upload_limit=1,
        chunk_size=64,
    )

    assert file_id == "FILEID"
    assert [call["index"] for call in part_calls] == [1, 2, 3]
    assert part_calls[-1]["file_base64_content"] == "eHl6"
