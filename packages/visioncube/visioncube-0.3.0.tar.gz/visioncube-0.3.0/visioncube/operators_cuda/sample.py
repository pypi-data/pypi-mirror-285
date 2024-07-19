#!/usr/bin/python3
# -*- coding:utf-8 -*-

"""
author：yannan1
since：2023-09-22
"""
import torch
import cv2 as cv
import numpy as np

from ..common import AbstractSample
from ..functional_cuda.imageio import hwc_to_chw, chw_to_hwc


class Sample(AbstractSample):

    def __init__(self, doc):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        super().__init__(doc)

    def _handle_image(self, image):

        image = torch.from_numpy(image).to(self.device)
        image = hwc_to_chw(image)

        return image

    def _handle_mask(self, mask):

        if isinstance(mask, bytes):
            mask = cv.imdecode(np.frombuffer(mask, np.byte), cv.IMREAD_GRAYSCALE)
        return torch.from_numpy(mask).unsqueeze(0).to(self.device)

    def _handle_bboxes(self, bboxes):
        return torch.tensor(bboxes).to(self.device)

    def _handle_heatmap(self, heatmap):

        heatmap = torch.from_numpy(heatmap).to(self.device)
        heatmap = hwc_to_chw(heatmap)

        return heatmap

    def _handle_keypoints(self, keypoints):
        return torch.tensor(keypoints).to(self.device)

    def _out_image(self):
        return chw_to_hwc(self.image).cpu().numpy()

    def _out_mask(self):
        return self.mask.squeeze(0).to(torch.int32).cpu().numpy()

    def _out_bboxes(self):
        return self.bboxes.cpu().numpy()

    def _out_heatmap(self):
        return chw_to_hwc(self.heatmap).cpu().numpy()

    def _out_keypoints(self):
        return self.keypoints.cpu().numpy()
