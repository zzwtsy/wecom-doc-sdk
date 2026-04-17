from __future__ import annotations

import base64

from ..client import WeComClient
from ..exceptions import WeComRequestError
from ..models.uploads import InitFileUploadRequest, UploadFileRequest

WEDRIVE_SIMPLE_UPLOAD_LIMIT = 10 * 1024 * 1024
WEDRIVE_CHUNK_SIZE = 2 * 1024 * 1024
WEDRIVE_MAX_FILE_SIZE = 20 * 1024 * 1024 * 1024


def _left_rotate(value: int, shift: int) -> int:
    """执行 32 位左循环移位。"""

    return ((value << shift) | (value >> (32 - shift))) & 0xFFFFFFFF


def _process_sha1_chunk(
    chunk: bytes, h0: int, h1: int, h2: int, h3: int, h4: int
) -> tuple[int, int, int, int, int]:
    """处理单个 64 字节 sha1 数据块。"""

    words = [0] * 80
    for index in range(16):
        offset = index * 4
        words[index] = int.from_bytes(chunk[offset : offset + 4], "big")

    for index in range(16, 80):
        words[index] = _left_rotate(
            words[index - 3] ^ words[index - 8] ^ words[index - 14] ^ words[index - 16],
            1,
        )

    a, b, c, d, e = h0, h1, h2, h3, h4
    for index in range(80):
        if index < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif index < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif index < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6

        temp = (_left_rotate(a, 5) + f + e + k + words[index]) & 0xFFFFFFFF
        a, b, c, d, e = temp, a, _left_rotate(b, 30), c, d

    return (
        (h0 + a) & 0xFFFFFFFF,
        (h1 + b) & 0xFFFFFFFF,
        (h2 + c) & 0xFFFFFFFF,
        (h3 + d) & 0xFFFFFFFF,
        (h4 + e) & 0xFFFFFFFF,
    )


class _SHA1Accumulator:
    """支持导出中间 state 的 sha1 计算器。

    企业微信分块上传要求非最后一块传入 sha1 的中间 state，而不是普通的最终 digest。
    Python 标准库不会暴露这个中间 state，这里按 sha1 规范补一个仅供内部使用的实现。
    """

    def __init__(self) -> None:
        self._state = (
            0x67452301,
            0xEFCDAB89,
            0x98BADCFE,
            0x10325476,
            0xC3D2E1F0,
        )
        self._unprocessed = b""
        self._message_byte_length = 0

    def update(self, data: bytes) -> None:
        """增量写入待计算内容。"""

        self._message_byte_length += len(data)
        buffer = self._unprocessed + data
        chunked_length = len(buffer) - (len(buffer) % 64)
        for offset in range(0, chunked_length, 64):
            self._state = _process_sha1_chunk(
                buffer[offset : offset + 64], *self._state
            )
        self._unprocessed = buffer[chunked_length:]

    def state_hexdigest(self) -> str:
        """返回当前中间 state 的十六进制表示。"""

        if self._unprocessed:
            raise ValueError("sha1 中间 state 仅能在 64 字节边界上导出")
        return "".join(f"{value:08x}" for value in self._state)

    def final_hexdigest(self) -> str:
        """返回当前累计内容的最终 sha1。"""

        h0, h1, h2, h3, h4 = self._state
        total_bits = self._message_byte_length * 8
        buffer = self._unprocessed + b"\x80"
        padding_length = (56 - (len(buffer) % 64)) % 64
        buffer += b"\x00" * padding_length
        buffer += total_bits.to_bytes(8, "big")

        for offset in range(0, len(buffer), 64):
            h0, h1, h2, h3, h4 = _process_sha1_chunk(
                buffer[offset : offset + 64], h0, h1, h2, h3, h4
            )
        return "".join(f"{value:08x}" for value in (h0, h1, h2, h3, h4))


class SmartSheetUploadHelper:
    """封装智能表格附件写入所依赖的微盘上传基础设施。"""

    def __init__(self, client: WeComClient) -> None:
        self._client = client

    @staticmethod
    def encode_file_content(file_bytes: bytes) -> str:
        """将文件内容编码为企业微信要求的 Base64 字符串。"""

        return base64.b64encode(file_bytes).decode("ascii")

    @staticmethod
    def split_file_bytes(file_bytes: bytes, *, chunk_size: int) -> list[bytes]:
        """按给定分块大小切分文件内容。"""

        return [
            file_bytes[offset : offset + chunk_size]
            for offset in range(0, len(file_bytes), chunk_size)
        ]

    @classmethod
    def calculate_block_sha(cls, chunks: list[bytes]) -> list[str]:
        """计算微盘分块上传所需的累积 sha1。"""

        digest = _SHA1Accumulator()
        block_sha: list[str] = []
        for index, chunk in enumerate(chunks, start=1):
            digest.update(chunk)
            if index == len(chunks):
                block_sha.append(digest.final_hexdigest())
            else:
                block_sha.append(digest.state_hexdigest())
        return block_sha

    def upload_file_bytes(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
        spaceid: str | None = None,
        fatherid: str | None = None,
        selected_ticket: str | None = None,
        simple_upload_limit: int = WEDRIVE_SIMPLE_UPLOAD_LIMIT,
        chunk_size: int = WEDRIVE_CHUNK_SIZE,
        max_file_size: int = WEDRIVE_MAX_FILE_SIZE,
    ) -> str:
        """根据文件大小选择微盘直传或分块上传。"""

        file_size = len(file_bytes)
        if file_size > max_file_size:
            raise ValueError("文件大小不能超过 20G")

        target_payload = {
            "spaceid": spaceid,
            "fatherid": fatherid,
            "selected_ticket": selected_ticket,
        }

        if file_size <= simple_upload_limit:
            upload_req = UploadFileRequest.model_validate(
                {
                    **target_payload,
                    "file_name": file_name,
                    "file_base64_content": self.encode_file_content(file_bytes),
                }
            )
            upload_resp = self._client.uploads.upload_file(upload_req)
            if not upload_resp.fileid:
                raise WeComRequestError("上传文件成功但响应缺少 fileid")
            return upload_resp.fileid

        chunks = self.split_file_bytes(file_bytes, chunk_size=chunk_size)
        init_req = InitFileUploadRequest.model_validate(
            {
                **target_payload,
                "file_name": file_name,
                "size": file_size,
                "block_sha": self.calculate_block_sha(chunks),
            }
        )
        init_resp = self._client.uploads.init_file_upload(init_req)
        if init_resp.hit_exist:
            if not init_resp.fileid:
                raise WeComRequestError("分块上传初始化命中秒传但响应缺少 fileid")
            return init_resp.fileid

        if not init_resp.upload_key:
            raise WeComRequestError("分块上传初始化成功但响应缺少 upload_key")

        for index, chunk in enumerate(chunks, start=1):
            self._client.uploads.upload_file_part(
                {
                    "upload_key": init_resp.upload_key,
                    "index": index,
                    "file_base64_content": self.encode_file_content(chunk),
                }
            )

        finish_resp = self._client.uploads.finish_file_upload(
            {"upload_key": init_resp.upload_key}
        )
        if not finish_resp.fileid:
            raise WeComRequestError("分块上传完成但响应缺少 fileid")
        return finish_resp.fileid


__all__ = [
    "SmartSheetUploadHelper",
    "WEDRIVE_CHUNK_SIZE",
    "WEDRIVE_MAX_FILE_SIZE",
    "WEDRIVE_SIMPLE_UPLOAD_LIMIT",
]
