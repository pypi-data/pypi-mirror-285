#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright(C) 2023 baidu, Inc. All Rights Reserved

# @Time : 2023/10/27 15:57
# @File : artifact_api_artifact.py
# @Software: PyCharm
"""
from enum import Enum
from typing import List, Optional, Dict, Any
import re
from bceinternalsdk.client.validator import Naming, parse_object_name

name_regex = re.compile(r"^(?P<object_name>.+?)(?:/versions/(?P<version>.+?))?$")


class Alias(Enum):
    """
    Alias
    """

    DEFAULT = "default"
    LATEST = "latest"
    BEST = "best"


class LocationStyle(Enum):
    """
    LocationStyle
    """
    DEFAULT = "Default"
    TRITON = "Triton"


def get_location_path(base_path: str, location_style: str, version: str):
    """
    get location path
    """
    if location_style == LocationStyle.TRITON.value:
        return f"{base_path}/{version}"

    return f"{base_path}/versions/{version}"


class ArtifactContent:
    """
    artifact content class
    """

    def __init__(self, uri: Optional[str] = "",
                 description: Optional[str] = "",
                 alias: Optional[list] = list(),
                 tags: Optional[dict] = dict(),
                 metadata: Optional = None):
        """
        init
        Args:
            uri: uri 版本文件路径
            description: 版本描述
            alias: 版本别名，如default, latest
            tags: 版本标签 [key:value]
            metadata: 版本基本信息
        """
        self.uri = uri
        self.description = description
        self.alias = alias
        self.tags = tags
        self.metadata = metadata


class ArtifactName:
    """
    ArtifactName
    """

    def __init__(self, object_name: str, version: str):
        """
        init
        Args:
            object_name: ObjectName 数据完整名称
            version: 版本
        """
        self.object_name = object_name
        self.version = version


def get_name(object_name: str, version: int) -> str:
    """
    get_name
    Args:
        object_name:
        version:
    Returns:
    """
    return object_name + "/versions/" + str(version)


class Artifact:
    """
    Artifact
    """

    def __init__(self,
                 naming: Optional[Naming] = None,
                 id=None,
                 name=None,
                 description=None,
                 version=None,
                 alias=None,
                 uri=None,
                 metadata=None,
                 tags=None,
                 create_at=None,
                 update_at=None,
                 delete_at=None):
        self.naming = naming
        self.id = id
        self.name = name
        self.description = description
        self.version = version
        self.alias = alias
        self.uri = uri
        self.metadata = metadata
        self.tags = tags
        self.create_at = create_at
        self.update_at = update_at
        self.delete_at = delete_at


def parse_artifact(name) -> Optional[Artifact]:
    """
    new_artifact_with_name
    Args:
        name:

    Returns:

    """
    artifact_name = parse_artifact_name(name)
    if artifact_name is None:
        return None
    n = parse_object_name(artifact_name.object_name)
    if n is None:
        return None
    artifact = Artifact(naming=n, name=name)
    try:
        version = int(artifact_name.version)
        artifact.version = version if version > 0 else None
    except ValueError:
        artifact.alias = artifact_name.version
    return artifact


def parse_artifact_name(name) -> Optional[ArtifactName]:
    """
    new_artifact_name
    Args:
        name: artifact_name

    Returns:

    """
    m = name_regex.search(name)
    if not m:
        return None
    if m.group("object_name") is None:
        return None
    if m.group("version") is None:
        return None
    return ArtifactName(
        object_name=m.group("object_name"),
        version=m.group("version")
    )

