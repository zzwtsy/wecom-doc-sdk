from __future__ import annotations

from typing import Callable

import pytest
from pydantic import ValidationError

from wecom_doc_sdk import WeComClient
from wecom_doc_sdk.models.enums import WedriveFileType
from wecom_doc_sdk.models.uploads import (
    AddSpaceAclRequest,
    CreateFileRequest,
    CreateSpaceAuthInfo,
    CreateSpaceRequest,
    DeleteSpaceAclAuthInfo,
    DeleteSpaceAclRequest,
    FinishFileUploadRequest,
    GetSpaceInfoRequest,
    InitFileUploadRequest,
    UploadFilePartRequest,
    UploadFileRequest,
    UploadImageRequest,
)


def test_upload_image_serializes_model_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """上传图片应命中正确路径并序列化请求。"""

    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "url": "https://example.com/image.png",
            "height": 100,
            "width": 120,
            "size": 1024,
        }
    )

    response = client.uploads.upload_image(
        UploadImageRequest(docid="DOCID", base64_content="BASE64DATA")
    )

    assert response.url == "https://example.com/image.png"
    assert response.height == 100
    assert response.width == 120
    assert response.size == 1024
    assert captured["path"] == "/cgi-bin/wedoc/image_upload"
    assert captured["json"] == {"docid": "DOCID", "base64_content": "BASE64DATA"}


def test_upload_image_accepts_dict_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """上传图片应支持 dict 入参并正确透传字段。"""
    captured = bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "url": "https://example.com/image.png",
            "height": 100,
            "width": 120,
            "size": 1024,
        }
    )

    response = client.uploads.upload_image(
        {"docid": "DOCID", "base64_content": "BASE64DATA"}
    )

    assert response.url == "https://example.com/image.png"
    assert response.height == 100
    assert response.width == 120
    assert response.size == 1024
    assert captured["path"] == "/cgi-bin/wedoc/image_upload"
    assert captured["json"] == {"docid": "DOCID", "base64_content": "BASE64DATA"}


def test_upload_file_serializes_model_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """上传微盘文件应命中正确路径并序列化请求。"""

    captured = bind_request_json({"errcode": 0, "errmsg": "ok", "fileid": "FILEID"})

    response = client.uploads.upload_file(
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        }
    )

    assert response.fileid == "FILEID"
    assert captured["path"] == "/cgi-bin/wedrive/file_upload"
    assert captured["json"] == {
        "spaceid": "SPACEID",
        "fatherid": "FOLDERID",
        "file_name": "example.txt",
        "file_base64_content": "BASE64DATA",
    }


def test_share_file_serializes_dict_request(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """获取微盘文件分享链接应命中正确路径并正确序列化请求。"""

    captured = bind_request_json(
        {"errcode": 0, "errmsg": "ok", "share_url": "https://example.com/share"}
    )

    response = client.uploads.share_file({"fileid": "FILEID"})

    assert response.share_url == "https://example.com/share"
    assert captured["path"] == "/cgi-bin/wedrive/file_share"
    assert captured["json"] == {"fileid": "FILEID"}


@pytest.mark.parametrize(
    ("api_call", "request_payload", "response_payload", "expected_path"),
    [
        (
            "create_space",
            {"space_name": "项目资料", "space_sub_type": 0},
            {"errcode": 0, "errmsg": "ok", "spaceid": "SPACEID"},
            "/cgi-bin/wedrive/space_create",
        ),
        (
            "create_file",
            {
                "spaceid": "SPACEID",
                "fatherid": "SPACEID",
                "file_type": WedriveFileType.FOLDER,
                "file_name": "附件目录",
            },
            {"errcode": 0, "errmsg": "ok", "fileid": "FILEID"},
            "/cgi-bin/wedrive/file_create",
        ),
        (
            "add_space_acl",
            {
                "spaceid": "SPACEID",
                "auth_info": [{"type": 1, "userid": "zhangsan", "auth": 7}],
            },
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedrive/space_acl_add",
        ),
        (
            "delete_space_acl",
            {
                "spaceid": "SPACEID",
                "auth_info": [{"type": 1, "userid": "zhangsan"}],
            },
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedrive/space_acl_del",
        ),
        (
            "get_space_info",
            {"spaceid": "SPACEID"},
            {
                "errcode": 0,
                "errmsg": "ok",
                "space_info": {
                    "spaceid": "SPACEID",
                    "space_name": "项目资料",
                    "auth_list": {"auth_info": [], "quit_userid": []},
                    "space_sub_type": 0,
                },
            },
            "/cgi-bin/wedrive/space_info",
        ),
        (
            "init_file_upload",
            {
                "spaceid": "SPACEID",
                "fatherid": "FOLDERID",
                "file_name": "example.bin",
                "size": 5,
                "block_sha": ["a9993e364706816aba3e25717850c26c9cd0d89d"],
            },
            {
                "errcode": 0,
                "errmsg": "ok",
                "hit_exist": False,
                "upload_key": "UPLOAD_KEY",
            },
            "/cgi-bin/wedrive/file_upload_init",
        ),
        (
            "upload_file_part",
            {
                "upload_key": "UPLOAD_KEY",
                "index": 1,
                "file_base64_content": "QUJD",
            },
            {"errcode": 0, "errmsg": "ok"},
            "/cgi-bin/wedrive/file_upload_part",
        ),
        (
            "finish_file_upload",
            {"upload_key": "UPLOAD_KEY"},
            {"errcode": 0, "errmsg": "ok", "fileid": "FILEID"},
            "/cgi-bin/wedrive/file_upload_finish",
        ),
    ],
)
def test_extended_upload_apis_support_model_and_dict_requests(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
    api_call: str,
    request_payload: dict[str, object],
    response_payload: dict[str, object],
    expected_path: str,
) -> None:
    """新增上传相关 API 应支持 dict 入参并命中正确路径。"""

    captured = bind_request_json(response_payload)
    response = getattr(client.uploads, api_call)(request_payload)

    assert response.ok is True
    assert captured["path"] == expected_path
    assert captured["json"] == {
        key: (value.value if isinstance(value, WedriveFileType) else value)
        for key, value in request_payload.items()
    }


@pytest.mark.parametrize(
    ("api_call", "request_model", "response_payload", "expected_json"),
    [
        (
            "create_space",
            CreateSpaceRequest(space_name="项目资料", space_sub_type=0),
            {"errcode": 0, "errmsg": "ok", "spaceid": "SPACEID"},
            {"space_name": "项目资料", "space_sub_type": 0},
        ),
        (
            "create_file",
            CreateFileRequest(
                spaceid="SPACEID",
                fatherid="SPACEID",
                file_type=WedriveFileType.FOLDER,
                file_name="附件目录",
            ),
            {"errcode": 0, "errmsg": "ok", "fileid": "FILEID"},
            {
                "spaceid": "SPACEID",
                "fatherid": "SPACEID",
                "file_type": WedriveFileType.FOLDER.value,
                "file_name": "附件目录",
            },
        ),
        (
            "add_space_acl",
            AddSpaceAclRequest(
                spaceid="SPACEID",
                auth_info=[
                    CreateSpaceAuthInfo(type=1, userid="zhangsan", auth=7)
                ],
            ),
            {"errcode": 0, "errmsg": "ok"},
            {
                "spaceid": "SPACEID",
                "auth_info": [{"type": 1, "userid": "zhangsan", "auth": 7}],
            },
        ),
        (
            "delete_space_acl",
            DeleteSpaceAclRequest(
                spaceid="SPACEID",
                auth_info=[DeleteSpaceAclAuthInfo(type=1, userid="zhangsan")],
            ),
            {"errcode": 0, "errmsg": "ok"},
            {
                "spaceid": "SPACEID",
                "auth_info": [{"type": 1, "userid": "zhangsan"}],
            },
        ),
        (
            "get_space_info",
            GetSpaceInfoRequest(spaceid="SPACEID"),
            {
                "errcode": 0,
                "errmsg": "ok",
                "space_info": {
                    "spaceid": "SPACEID",
                    "space_name": "项目资料",
                    "auth_list": {"auth_info": [], "quit_userid": []},
                    "space_sub_type": 0,
                },
            },
            {"spaceid": "SPACEID"},
        ),
        (
            "init_file_upload",
            InitFileUploadRequest(
                spaceid="SPACEID",
                fatherid="FOLDERID",
                file_name="example.bin",
                size=5,
                block_sha=["sha1"],
            ),
            {"errcode": 0, "errmsg": "ok", "hit_exist": False, "upload_key": "UP"},
            {
                "spaceid": "SPACEID",
                "fatherid": "FOLDERID",
                "file_name": "example.bin",
                "size": 5,
                "block_sha": ["sha1"],
            },
        ),
        (
            "upload_file_part",
            UploadFilePartRequest(
                upload_key="UPLOAD_KEY", index=1, file_base64_content="QUJD"
            ),
            {"errcode": 0, "errmsg": "ok"},
            {
                "upload_key": "UPLOAD_KEY",
                "index": 1,
                "file_base64_content": "QUJD",
            },
        ),
        (
            "finish_file_upload",
            FinishFileUploadRequest(upload_key="UPLOAD_KEY"),
            {"errcode": 0, "errmsg": "ok", "fileid": "FILEID"},
            {"upload_key": "UPLOAD_KEY"},
        ),
    ],
)
def test_extended_upload_apis_support_model_requests(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
    api_call: str,
    request_model: object,
    response_payload: dict[str, object],
    expected_json: dict[str, object],
) -> None:
    """新增上传相关 API 应支持模型对象入参。"""

    captured = bind_request_json(response_payload)
    response = getattr(client.uploads, api_call)(request_model)

    assert response.ok is True
    assert captured["json"] == expected_json


@pytest.mark.parametrize(
    "payload",
    [
        {
            "spaceid": "SPACEID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        {
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        {
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "selected_ticket": "TICKET",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        },
    ],
)
def test_upload_file_request_rejects_invalid_target_group(
    payload: dict[str, str],
) -> None:
    """上传文件请求应严格校验目标参数组合。"""

    with pytest.raises(ValidationError):
        UploadFileRequest.model_validate(payload)


def test_upload_file_request_accepts_space_and_father_group() -> None:
    """上传文件请求在 spaceid 与 fatherid 同时提供时应校验通过。"""

    request = UploadFileRequest.model_validate(
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        }
    )
    assert request.spaceid == "SPACEID"
    assert request.fatherid == "FOLDERID"


def test_upload_file_request_accepts_selected_ticket_group() -> None:
    """上传文件请求在 selected_ticket 模式下应校验通过。"""

    request = UploadFileRequest.model_validate(
        {
            "selected_ticket": "TICKET",
            "file_name": "example.txt",
            "file_base64_content": "BASE64DATA",
        }
    )
    assert request.selected_ticket == "TICKET"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "spaceid": "SPACEID",
            "file_name": "example.bin",
            "size": 10,
            "block_sha": ["abc"],
        },
        {
            "fatherid": "FOLDERID",
            "file_name": "example.bin",
            "size": 10,
            "block_sha": ["abc"],
        },
        {
            "spaceid": "SPACEID",
            "fatherid": "FOLDERID",
            "selected_ticket": "TICKET",
            "file_name": "example.bin",
            "size": 10,
            "block_sha": ["abc"],
        },
    ],
)
def test_init_file_upload_request_rejects_invalid_target_group(
    payload: dict[str, object],
) -> None:
    """分块上传初始化请求应复用上传目标参数校验。"""

    with pytest.raises(ValidationError):
        InitFileUploadRequest.model_validate(payload)


def test_init_file_upload_request_accepts_selected_ticket_group() -> None:
    """分块上传初始化请求应支持 selected_ticket 模式。"""

    request = InitFileUploadRequest.model_validate(
        {
            "selected_ticket": "TICKET",
            "file_name": "example.bin",
            "size": 10,
            "block_sha": ["abc"],
        }
    )
    assert request.selected_ticket == "TICKET"


def test_create_file_request_validates_file_type_enum() -> None:
    """创建微盘文件请求应拒绝非法 file_type。"""

    with pytest.raises(ValidationError):
        CreateFileRequest.model_validate(
            {
            "spaceid": "SPACEID",
            "fatherid": "SPACEID",
            "file_type": 999,
            "file_name": "附件目录",
            }
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"type": 1, "auth": 7},
        {"type": 2, "userid": "zhangsan", "departmentid": 1, "auth": 1},
        {"type": 2, "departmentid": 1, "auth": 7},
        {"type": 3, "userid": "zhangsan", "auth": 1},
    ],
)
def test_create_space_auth_info_rejects_invalid_member_scope(
    payload: dict[str, object],
) -> None:
    """空间成员授权信息应校验成员范围与权限组合。"""

    with pytest.raises(ValidationError):
        CreateSpaceAuthInfo.model_validate(payload)


def test_create_space_auth_info_accepts_user_scope() -> None:
    """空间成员授权信息应支持成员类型。"""

    auth_info = CreateSpaceAuthInfo.model_validate(
        {"type": 1, "userid": "zhangsan", "auth": 7}
    )
    assert auth_info.userid == "zhangsan"


@pytest.mark.parametrize(
    "payload",
    [
        {"type": 1},
        {"type": 1, "userid": "zhangsan", "departmentid": 1},
        {"type": 2},
        {"type": 2, "userid": "zhangsan", "departmentid": 1},
        {"type": 3, "userid": "zhangsan"},
    ],
)
def test_delete_space_acl_auth_info_rejects_invalid_member_scope(
    payload: dict[str, object],
) -> None:
    """空间成员移除信息应校验成员范围。"""

    with pytest.raises(ValidationError):
        DeleteSpaceAclAuthInfo.model_validate(payload)


def test_delete_space_acl_auth_info_accepts_department_scope() -> None:
    """空间成员移除信息应支持部门类型。"""

    auth_info = DeleteSpaceAclAuthInfo.model_validate(
        {"type": 2, "departmentid": 1}
    )
    assert auth_info.departmentid == 1


def test_get_space_info_parses_nested_space_info(
    client: WeComClient,
    bind_request_json: Callable[[dict[str, object]], dict[str, object]],
) -> None:
    """获取空间信息应正确解析空间详情与成员列表。"""

    bind_request_json(
        {
            "errcode": 0,
            "errmsg": "ok",
            "space_info": {
                "spaceid": "SPACEID",
                "space_name": "项目资料",
                "auth_list": {
                    "auth_info": [
                        {"type": 1, "userid": "zhangsan", "auth": 7},
                        {"type": 2, "departmentid": 1, "auth": 1},
                    ],
                    "quit_userid": ["lisi"],
                },
                "space_sub_type": 0,
            },
        }
    )

    response = client.uploads.get_space_info({"spaceid": "SPACEID"})

    assert response.space_info is not None
    assert response.space_info.spaceid == "SPACEID"
    assert response.space_info.space_name == "项目资料"
    assert response.space_info.space_sub_type == 0
    assert response.space_info.auth_list is not None
    assert response.space_info.auth_list.quit_userid == ["lisi"]
    assert response.space_info.auth_list.auth_info is not None
    assert response.space_info.auth_list.auth_info[0].userid == "zhangsan"
    assert response.space_info.auth_list.auth_info[1].departmentid == 1
