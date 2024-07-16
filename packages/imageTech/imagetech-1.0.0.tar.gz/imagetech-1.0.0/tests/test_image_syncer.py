import pytest
import os
import cv2
import numpy as np

from imageTech.image_syncer import ImageProcessor


@pytest.fixture(scope="module")
def setup_images():
    # Define directories
    input_dir = os.path.abspath('test_images')
    output_dir = os.path.abspath('output')

    # print(f"Input directory: {input_dir}")
    # print(f"Output directory: {output_dir}")

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create test images if they do not exist
    image1_path = os.path.join(input_dir, 'img_prep_1.png')
    image2_path = os.path.join(input_dir, 'img_prep_2.png')

    if not os.path.exists(image1_path):
        image1 = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(image1_path, image1)
        # print(f"Created image: {image1_path}")

    if not os.path.exists(image2_path):
        image2 = np.zeros((100, 100, 3), dtype=np.uint8)
        image2[50:] = [255, 255, 255]  # Add a white rectangle in the second image
        cv2.imwrite(image2_path, image2)
        # print(f"Created image: {image2_path}")

    # Verify the images are created successfully
    assert os.path.exists(image1_path), f"Test image {image1_path} was not created."
    assert os.path.exists(image2_path), f"Test image {image2_path} was not created."

    yield input_dir, output_dir, image1_path, image2_path

    # Cleanup output directory after tests
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))


def test_display_difference(setup_images):
    input_dir, output_dir, image1_path, image2_path = setup_images
    img_p = ImageProcessor()

    # print(f"Testing display difference with images: {image1_path} and {image2_path}")
    img_p.display_difference(image1_path, image2_path, output_dir, is_cv_read=False)

    # Verify that the output image is created
    output_image_path = os.path.join(output_dir, 'image_difference.png')
    assert os.path.exists(output_image_path), "Output image not found."

    # Load the output image
    output_image = cv2.imread(output_image_path)
    assert output_image is not None, "Failed to read the output image."

    # Check that the output image has red highlights where the differences are
    red_mask = np.all(output_image == [0, 0, 255], axis=-1)
    assert np.any(red_mask), "No differences highlighted in red."
