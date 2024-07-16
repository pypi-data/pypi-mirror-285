import os
import cv2

from collections import Counter
from PIL import Image

from imageTech.logs import LoggerConfig


class ImageProcessor(object):
    def __init__(self):
        self.__logger = LoggerConfig('ImageProcessor').get_logger()

    def display_difference(self, image1, image2, output_directory=None, is_cv_read=False):
        """
        Display and save the diff between two images.

        Parameters:
        - image1 (str or ndarray): Path to the first image or the image array.
        - image2 (str or ndarray): Path to the second image or the image array.
        - is_cv_read (bool): If True, the images are already read using cv2.
        - output_directory (str): Path to the directory where the result should be saved.
        """
        try:
            if not output_directory:
                raise Exception("ParameterException: Invalid directory path. Provide a proper directory path")

            # Read images if not already read
            if not is_cv_read:
                try:
                    image1 = cv2.imread(image1)
                    image2 = cv2.imread(image2)
                except Exception as e:
                    raise Exception(f"ImageReadException: Could not read one or both images {e}")
                if image1 is None or image2 is None:
                    raise Exception("ImageReadException: Could not read one or both images")

            # Compute the difference
            try:
                diff = cv2.subtract(image1, image2)
            except Exception as de:
                raise Exception(f"ImageDiffException: Images must be of same size {de}")

            # Convert to grayscale and create a red mask
            conv_hsv_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(conv_hsv_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

            # Highlight differences in red
            diff[mask != 255] = [0, 0, 255]
            image1[mask != 255] = [0, 0, 255]
            image2[mask != 255] = [0, 0, 255]

            # Create the directory if it doesn't exist
            try:
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)
            except Exception as e:
                raise Exception(f"Invalid directory path. Could not create directory {e}")

            # Save the diff image
            diff_filename = os.path.join(output_directory, 'image_difference.png')
            cv2.imwrite(diff_filename, diff)
        except Exception as e:
            self.__logger.info(f'DisplayDiffError: {e}')
