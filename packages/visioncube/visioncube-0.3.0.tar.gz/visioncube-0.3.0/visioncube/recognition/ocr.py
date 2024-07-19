#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
author：yannan1
since：2023-06-06
"""

from typing import Tuple, Optional

import numpy as np

from visioncube.common import AbstractTransform

__all__ = [
    'EasyOCR',
    'CnOCR',
]


class EasyOCR(AbstractTransform):

    def __init__(self, lang: str = 'ch_sim', use_gpu=False, model_root: Optional[str] = None, **kwargs) -> None:
        """EasyOCR, 字符识别, 识别

        Args:
            lang: Language codes, 识别语言, {"ch_sim", "en", "ko", "ja"}, "ch_sim"
            use_gpu: Whether to use gpu, 是否使用GPU, {True, False}, False
            model_root: model root path, 模型文件根目录, {}, None
        """
        super().__init__(use_gpu=False)

        try:
            import easyocr
        except ImportError:
            raise RuntimeError(
                'The OCR module requires "easyocr" package. '
                'You should install it by "pip install easyocr".'
            )

        def _reformat_input(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
            if len(image.shape) == 2:
                return np.tile(image[:, :, None], (1, 1, 3)), image
            elif len(image.shape) == 3:
                if image.shape[-1] == 1:
                    return np.tile(image, (1, 1, 3)), image[:, :, 0]
                elif image.shape[-1] == 3:
                    return image, np.mean(image, -1).astype(np.uint8)
            raise RuntimeError(f'Invalid image shape {image.shape}.')

        setattr(easyocr.easyocr, 'reformat_input', _reformat_input)
        self.reader = easyocr.Reader([lang], gpu=use_gpu, model_storage_directory=model_root, **kwargs)

    def _apply(self, sample):

        if sample.image is None:
            return sample

        result = self.reader.readtext(sample.image)

        ocr_out = []
        for item in result:
            ocr_out.append({
                "text": item[1],
                "text_score": item[2],
                "position": item[0],
            })
        sample.ocr = ocr_out

        return sample


class CnOCR(AbstractTransform):

    def __init__(
            self,
            rec_root: Optional[str] = None,
            det_root: Optional[str] = None,
            rec_model_name: Optional[str] = "densenet_lite_136-gru",
            det_model_name: Optional[str] = "ch_PP-OCRv3_det",
            use_gpu: bool = False,
            **kwargs
    ) -> None:
        """CnOCR, 光学字符识别, 识别

        Args:
            rec_root: Rec model root path, 识别模型文件根目录, {}, None
            det_root: Det model root path, 检测模型文件根目录, {}, None
            rec_model_name: Rec Model Name, 识别模型名称, {"densenet_lite_136-gru", "scene-densenet_lite_136-gru", "doc-densenet_lite_136-gru", "number-densenet_lite_136-fc", "ch_PP-OCRv3", "en_PP-OCRv3", "en_number_mobile_v2.0", "chinese_cht_PP-OCRv3"}, "densenet_lite_136-gru"
            det_model_name: Det Model Name, 检测模型名称, {"db_shufflenet_v2", "db_shufflenet_v2_small", "db_shufflenet_v2_tiny", "db_mobilenet_v3", "db_mobilenet_v3_small", "db_resnet34", "db_resnet18", "ch_PP-OCRv3_det", "ch_PP-OCRv2_det", "en_PP-OCRv3_det"}, "ch_PP-OCRv3_det"
            use_gpu: Whether to use gpu, 是否使用GPU, {True, False}, False
        """

        """
        det_model_name:
        - db_shufflenet_v2      : 简体中文、繁体英文、英文、数字
        - db_shufflenet_v2_small: 简体中文、繁体英文、英文、数字
        - db_shufflenet_v2_tiny : 简体中文、繁体英文、英文、数字
        - db_mobilenet_v3       : 简体中文、繁体英文、英文、数字
        - db_mobilenet_v3_small : 简体中文、繁体英文、英文、数字
        - db_resnet34           : 简体中文、繁体英文、英文、数字
        - db_resnet18           : 简体中文、繁体英文、英文、数字
        - ch_PP-OCRv3_det       : 简体中文、繁体英文、英文、数字
        - ch_PP-OCRv2_det       : 简体中文、繁体英文、英文、数字
        - en_PP-OCRv3_det       : 英文、数字
        - naive_det             : 排版简单的印刷体文件图片(速度快，对图片较挑剔)

        rec_model_name
        - densenet_lite_136-gru      : 简体中文、英文、数字
        - scene-densenet_lite_136-gru: 简体中文、英文、数字（场景图片，识别识别一般拍照图片中的文字）
        - doc-densenet_lite_136-gru  : 简体中文、英文、数字（文档图片，适合识别规则文档的截图图片）
        - number-densenet_lite_136-fc: 纯数字（仅包含 0~9 十个数字）
        - ch_PP-OCRv3                : 简体中文、英文、数字
        - ch_ppocr_mobile_v2.0       : 简体中文、英文、数字
        - en_PP-OCRv3                : 英文、数字
        - en_number_mobile_v2.0      : 英文、数字
        - chinese_cht_PP-OCRv3       : 繁体中文、英文、数字

        """
        super().__init__(use_gpu=False)

        try:
            from cnocr import CnOcr
            from cnocr.utils import data_dir
            from cnstd.utils import data_dir as det_data_dir
        except ImportError:
            if use_gpu:
                raise RuntimeError(
                    'The OCR module requires "cnocr" package. '
                    'You should install it by "pip install cnocr[ort-gpu]==2.3".'
                )
            else:
                raise RuntimeError(
                    'The OCR module requires "cnocr" package. '
                    'You should install it by "pip install cnocr[ort-cpu]==2.3".'
                )

        rec_root = rec_root or data_dir()
        det_root = det_root or det_data_dir()

        self.reader = CnOcr(
            rec_root=rec_root,
            det_root=det_root,
            rec_model_name=rec_model_name,
            det_model_name=det_model_name,
            **kwargs
        )

    def _apply(self, sample):

        if sample.image is None:
            return sample

        result = self.reader.ocr(sample.image)

        ocr_out = []
        for item in result:
            ocr_out.append({
                "text": item['text'],
                "text_score": item['score'],
                "position": item["position"].astype(int).tolist(),
            })
        sample.ocr = ocr_out

        return sample


class OCR(AbstractTransform):

    def __init__(self, backend, *args, **kwargs):
        super().__init__(use_gpu=False)

        self.engine = None
        if backend == 'easyocr':
            self.engine = EasyOCR(*args, **kwargs)
        elif backend == 'cnocr':
            self.engine = CnOCR(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _apply(self, sample):
        return self.engine(sample)
