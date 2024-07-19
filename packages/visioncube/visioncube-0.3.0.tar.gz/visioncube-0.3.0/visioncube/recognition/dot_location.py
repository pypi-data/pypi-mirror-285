import numpy as np
import cv2 as cv

from visioncube.common import AbstractTransform


class DOTLocation(AbstractTransform):

    def __init__(
            self, 
            scale=4,
            rotate=True,
            color_level=True,
            position='mid',  # 'top' 'bottom'
            ceil=0.8,
            floor=0.75,
            step=25
    ) -> None:
        super().__init__(use_gpu=False)

        try:
            from paddleocr import PaddleOCR
        except ImportError:
            raise RuntimeError(
                'The OCR module requires "paddleocr" package. '
                'You should install it by "pip install paddleocr".'
            )

        self.model = PaddleOCR(use_angle_cls=True, lang="en")
        self.scale = scale
        self.rotate = rotate
        self.color_level = color_level
        self.position = position
        self.ceil = ceil
        self.floor = floor
        self.step = step
        self.win_len = self.step*10

    def _transform_image(self, img):
        # rotate image
        if self.rotate:
            img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        self.ori_img = img

        # resize & crop image
        h, w, _ = img.shape
        img  = cv.resize(img, (int(w/self.scale), int(h/self.scale)))
        h, _, _ = img.shape
        if self.position == 'mid':
            img = img[h//2-1:h//2-1+h//4, :, :]
        elif self.position == 'top':
            img = img[h//4-1:h//2-1, :, :]
        elif self.position == 'bottom':
            img = img[h//2-1+h//4:, :, :]
        else:
            raise ValueError(f"Invalid value position='{self.position}'. Optional values: 'mid','top','bottom'")
        
        # adjust color level
        if self.color_level:
            in_black = np.array(20, dtype=np.float32)
            in_white = np.array(150, dtype=np.float32)
            gamma = np.array(1, dtype=np.float32)
            out_black = np.array(0, dtype=np.float32)
            out_white = np.array(255, dtype=np.float32)
            img = np.array(img, dtype=np.float32)

            img -= in_black
            img /= in_white - in_black
            np.clip(img, 0, 1, img)

            img **= 1 / gamma
            img *= out_white - out_black
            img += out_black
            np.clip(img, 0, 255, img)

        self.image = img

    def _convert_to_origin_coord(self, coord, win_idx):
        x = int(coord[0]) + win_idx
        h = self.image.shape[0]
        if self.position == 'mid':
            y = int(coord[1]) + h*2
        elif self.position == 'top':
            y = int(coord[1]) + h
        elif self.position == 'bottom':
            y = int(coord[1]) + h*3
        else:
            raise ValueError(f"Invalid value position='{self.position}'. Optional values: 'mid','top','bottom'")
        return x*self.scale, y*self.scale
    
    def _sliding_window(self):
        w = self.image.shape[1]
        max_conf = self.floor
        dot_flag = False
        for i in range(0, w, self.step):
            end = w-1 if i+self.win_len>w else i+self.win_len
            result = self.model.ocr(self.image[:, i:end, :], cls=True)[0]
            if result is None:
                continue
            for item in result:
                text = item[1][0]  # item['text']
                conf = item[1][1]  # item['text_score']
                bbox = item[0]  # item[2]
                if 'DOT' in text and conf>=max_conf:
                    dot_item = [text, conf, bbox, i]
                    max_conf = conf
                    dot_flag = True
                    break
            if max_conf >= self.ceil:
                break
        if dot_flag:
            x0, y0 = self._convert_to_origin_coord(dot_item[2][0], dot_item[-1])
            x2, y2 = self._convert_to_origin_coord(dot_item[2][2], dot_item[-1])
            self.result = [{
                'text': dot_item[0],
                'confidence': dot_item[1],
                'bbox': [x0, y0, x2, y2],
            }]
            self.win_start = dot_item[-1]
        else:
            self.result = []

    def _apply(self, sample):

        if sample.image is None:
            return sample
        
        self._transform_image(sample.image)
        self._sliding_window()
        sample.dot = self.result
        return sample
