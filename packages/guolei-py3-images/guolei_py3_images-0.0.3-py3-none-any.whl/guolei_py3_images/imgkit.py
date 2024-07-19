#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os

import imgkit
from addict import Dict


def str_to_image(
        output_path: str = "",
        content: str = "",
        imgkit_from_string_kwargs: dict = {},
):
    """
    字符串转图片
    :param output_path:图片输出文件路径
    :param content: 内容
    :param from_string_kwargs: imgkit.from_string(**from_string_kwargs)
    :return:
    """
    if not isinstance(output_path, str):
        raise TypeError(f"output_path must be type str")
    if not len(output_path):
        raise ValueError(f"output_path must be type str and not empty")
    if not isinstance(content, str):
        raise TypeError(f"content must be type str")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    imgkit_from_string_kwargs = Dict(imgkit_from_string_kwargs)
    imgkit_from_string_kwargs.setdefault("config", None)
    imgkit.from_string(
        output_path=output_path,
        string=content,
        **imgkit_from_string_kwargs,
    )
    return output_path
