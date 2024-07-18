#submodule2/module2.py
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from robot.api.deco import keyword

class XImages:
    @keyword('XCompare Images')
    def compare_images(self, image_path1, image_path2):
        """
        ***|    Description     |***
        |   *`XCompare Images`*   |   เปรียบเทียบภาพสองภาพและคืนค่าเปอร์เซ็นต์ความเหมือน |

        
        ***|    Example     |***
        | *`XCompare Images`* | *`path_to_image1.jpg`* | *`path_to_image2.jpg`* |


        ***|    Parameters     |***
        - **`image_path1`**: พาธของภาพแรกที่ต้องการเปรียบเทียบ
        - **`image_path2`**: พาธของภาพที่สองที่ต้องการเปรียบเทียบ

        ***|    Returns     |***
        - **`similarity_percentage`**: เปอร์เซ็นต์ความเหมือนของภาพสองภาพ

        *`Create By Tassana Khrueawan`*
        """
        # โหลดภาพทั้งสอง
        img1 = cv2.imread(image_path1)
        img2 = cv2.imread(image_path2)

        # ตรวจสอบว่าภาพถูกโหลดมาถูกต้องหรือไม่
        if img1 is None:
            raise ValueError(f"Cannot load image from path: {image_path1}")
        if img2 is None:
            raise ValueError(f"Cannot load image from path: {image_path2}")

        # ตรวจสอบว่าภาพมีขนาดเดียวกันหรือไม่
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions to be compared")

        # คำนวณความแตกต่างและค่าปกติ
        difference = cv2.absdiff(img1, img2)
        norm_diff = np.linalg.norm(difference)

        # คำนวณเปอร์เซ็นต์ความเหมือน
        norm_img1 = np.linalg.norm(img1)
        similarity = 1 - (norm_diff / norm_img1)
        similarity_percentage = similarity * 100

        return similarity_percentage
