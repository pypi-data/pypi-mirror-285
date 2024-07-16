import os
import json
import datetime

import cv2
from skimage.metrics import structural_similarity as ssim
from PIL import Image
from collections import Counter


class CompareFilmstrip(object):
    __INCREMENT = 250

    def __init__(self, directory, measurement_time=None, mobile_emulator=False):
        """
        Initialize the CompareFilmstrip object.

        Parameters:
        - directory (str): Path to the directory containing images and JSON files.
        - measurement_time: Process start time
        - mobile_emulator (bool): True if mobile device else False
        """
        self.__existing_images = []
        self.__removed_images = []
        self.__unique_images = []
        self.__timestamp_images = {}
        self.__directory = directory
        self.__filmstrip_directory = os.path.join(self.__directory, 'f')
        self.__json = None
        self.__first_image = None
        self.__second_image = None
        self.__last_frames = None
        self.__mobile_emulator = mobile_emulator
        if measurement_time:
            self.__process_start_time = measurement_time

        self.__tmp_image = None
        self.__fs_position = None
        self.__sample_ss_timestamp = 'Screenshot @ 2024-04-22 11:22:51 UTC    '
        self.__sample_fs_timestamp = 'Filmstrip @ 2024-04-22 11:22:33.218 - 2024-04-22 11:22:33.468 UTC  '
        self.__screenshot_text_size = None
        self.__filmstrip_text_size = None
        self.__ss_position = None

    def __compare_size(self):
        """
        Compare the size of two images.

        Returns:
        - bool: True if the size is different, False otherwise.
        """
        # Store the image shape into variable
        ori_shape = self.__first_image.shape[:2]
        dup_shape = self.__second_image.shape[:2]

        # TEST 1: Based on shape of image
        if ori_shape == dup_shape:
            # Image size is same
            return False
        else:
            print('Image size if different inserting both images')
            # Image is different in size
            return True

    def __compare_histogram(self):
        """
        Compare the histograms of two images.

        Converts images to HSV, calculates histograms, and compares them using correlation coefficient.
        A high similarity score (≥ 0.99) indicates equal histograms.

        Useful for assessing color similarity when pixel-wise differences may be less informative.

        Returns:
        - bool: True if the histograms are different, False otherwise.
        """
        hsv_base = cv2.cvtColor(self.__first_image, cv2.COLOR_BGR2HSV)
        hsv_test = cv2.cvtColor(self.__second_image, cv2.COLOR_BGR2HSV)

        h_bins = 50
        s_bins = 60
        hist_size = [h_bins, s_bins]
        h_ranges = [0, 180]
        s_ranges = [0, 256]
        ranges = h_ranges + s_ranges
        channels = [0, 1]

        hist_base = cv2.calcHist([hsv_base], channels, None, hist_size, ranges, accumulate=False)
        cv2.normalize(hist_base, hist_base, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        hist_test = cv2.calcHist([hsv_test], channels, None, hist_size, ranges, accumulate=False)
        cv2.normalize(hist_test, hist_test, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

        compare_method = cv2.HISTCMP_CORREL

        similarity_score = cv2.compareHist(hist_base, hist_test, compare_method)

        if similarity_score >= 0.99:
            # Histogram is equal. Image is same
            return False
        else:
            # Histogram is different
            return True

    def __detect_noise_and_artifacts(self):
        """
        Detect noise and artifacts in two images using structural similarity index.

        Converts images to grayscale, calculates SSIM index, and uses a threshold (0.9999) for comparison.
        Useful for spotting noise and artifacts in image pairs.

        Returns:
        - bool: True if images have noise and are different, False otherwise.
        """
        first_img = cv2.cvtColor(self.__first_image, cv2.COLOR_BGR2GRAY)
        second_img = cv2.cvtColor(self.__second_image, cv2.COLOR_BGR2GRAY)

        # Compute structural similarity index
        ssim_index, _ = ssim(first_img, second_img, full=True)

        ssim_threshold = 0.9999  # Adjusted as per blue and no clr image

        if ssim_index < ssim_threshold:
            # The images have noise so they are different
            return True
        else:
            # The images are relatively clean so they are same.
            return False

    def __fetch_image_names(self, session_id):
        """
        Fetch the names of images based on the session ID.

        Parameters:
        - session_id (str): session ID used to filter image names.
        """
        all_files = []

        # Check if the provided path is a directory
        if not os.path.isdir(self.__filmstrip_directory):
            print(f"{self.__filmstrip_directory} is not a valid directory.")
            return

        # options '.png', '.jpg', '.jpeg', '.gif', '.bmp' and index.json file for modifications
        valid_extensions = (".index.json", ".png", ".jpg", ".jpeg", ".gif", ".bmp")

        # Get a list of all files in the directory based on session_id and valid extensions
        for filename in os.scandir(self.__filmstrip_directory):
            if filename.is_file() and filename.name.endswith(valid_extensions):
                if session_id in filename.name:
                    all_files.append(filename.name)

        try:
            if len(all_files) > 2:
                self.__existing_images = sorted(all_files,
                                                key=self.__fetch_json_file)[1:]

            self.__fetch_lastframe_data()
        except Exception as e:
            print(f'Json file not found {e}')
        print(f'Images in filmstrip: {len(self.__existing_images)}')

    def __fetch_json_file(self, filename):
        """
        Fetch the JSON file associated with the session ID and reads json data to store original last frames

        Parameters:
            filename (str): Name of the file to check.

        Returns:
            tuple[int, str]: (error_code, filename)

                  - error_code (int): 0 for success, 1 for error.
                  - filename (str): The filename (unchanged).
        """

        if not filename.lower().endswith('.json'):
            return 1, filename  # Early return for non-JSON files

        try:
            json_file_path = os.path.join(self.__filmstrip_directory, filename)
            with open(json_file_path, 'r') as file:
                self.__json_file = filename
                self.__last_frames = json.load(file)
            return 0, filename

        except Exception as e:
            print(f'Error loading JSON file: {e}')
            return 1, filename

    def __fetch_lastframe_data(self):
        """
        Fetches the last frames from the original JSON data.
        Returns:
        None
        """
        last_frames = []
        if self.__last_frames:
            for step in self.__last_frames:
                last_frames.append(step.get('lastFrame'))
            self.__last_frames = last_frames

    def __process_first_two_images(self):
        """
        Process the first two images in the list and update unique_images and timestamp information.

        This method is called by __process_two_images() and is responsible for comparing the first two images,
        updating the unique_images list, and setting timestamps.
        """
        try:
            # Load the first two images
            self.__first_image = cv2.imread(f'{os.path.join(self.__filmstrip_directory, self.__existing_images[0])}')
            self.__second_image = cv2.imread(f'{os.path.join(self.__filmstrip_directory, self.__existing_images[1])}')
            # Check if the first two images are different
            if self.__compare_size():
                # If image size is different then insert both as unique
                self.__unique_images += [self.__existing_images[0], self.__existing_images[1]]

            elif self.__images_different():
                # Store the difference if they are different and insert both images
                # self.__display_difference(self.__existing_images[0], self.__existing_images[1])
                self.__unique_images += [self.__existing_images[0], self.__existing_images[1]]

            else:
                self.__removed_images.append(self.__existing_images[0])
                os.unlink(f'{self.__filmstrip_directory}/{self.__existing_images[0]}')
                # If the first two images are the same, add latest to unique_images
                self.__unique_images.append(self.__existing_images[1])
            self.__tmp_image = self.__second_image
        except Exception as e:
            print(f'Error comparing first two images')

    def __process_other_images(self, img):
        """
        Process a single image in the list, compare it with previous image and
        update unique_images, timestamp information.

        This method is called by __process_two_images() for each image in the list (starting from the third image).

        Parameters:
        - img (str): The filename of the image to be processed.

        Returns:
            bool: False if image is unique (not repeated) else True
        """

        repeated = False

        try:
            # Load the images to be compared
            self.__first_image = self.__tmp_image
            self.__second_image = cv2.imread(f'{os.path.join(self.__filmstrip_directory, img)}')
            if self.__compare_size():
                # If image size is different then insert both as unique
                self.__unique_images.append(img)

            # If image is different
            elif self.__images_different():
                # self.__display_difference(self.__unique_images[-1], img)
                self.__unique_images.append(img)
            else:
                # If the images are the same, update the last element in unique_images with the current image
                self.__removed_images.append(self.__unique_images[-1])
                os.unlink(f'{self.__filmstrip_directory}/{self.__unique_images[-1]}')
                self.__unique_images[-1] = img
                repeated = True

            self.__timestamp_images[img] = self.__process_start_time = self.__process_start_time + self.__INCREMENT
            self.__tmp_image = self.__second_image
        except Exception as e:
            print(f'Error comparing images')

        return repeated

    def __process_two_images(self):
        """
           Process the first two images and compare them with subsequent images in the list.

           This method performs the following steps:

           1. Checks if there are at least two existing images for comparison.
           2. Loads the first two images and compares them based on size and content differences.
           3. If the images have different sizes, both are marked as unique.
           4. If the images are different in content, both are marked as unique.
           5. If the images are the same, the latest image is added to the unique images, and the previous image is removed.
           6. Updates timestamp information for processed images.
           7. Iterates through the remaining images, comparing each with the last unique image.
           8. Adds images to the unique list based on differences in size or content.
           9. Updates timestamp information for processed images.
           10. Displays the count of unique and removed images.
           11. Updates last frames in index.json

           Note:
           - The comparison of images is done using internal methods such as __compare_size() and __images_different().
           - Duplicate images are removed from the file system.
           """
        # Check if there are any existing images
        if len(self.__existing_images) < 2:
            print("Insufficient images found for comparison.")
            return

        last_frame_counter = 1
        print('Processing images please wait!')
        # Check if there are any unique images
        if len(self.__unique_images) == 0:
            self.__process_first_two_images()
            last_frame_counter += 2

        try:
            self.__timestamp_images[self.__existing_images[0]] = self.__process_start_time
            self.__timestamp_images[
                self.__existing_images[1]] = self.__process_start_time = self.__process_start_time + self.__INCREMENT
        except Exception as e:
            print(f'Error while updating timestamps of first two images {e}')

        l_frames = []
        # Loop through the remaining images in the list
        for img in self.__existing_images[2:]:
            repeated = self.__process_other_images(img)

            # Process last frames counter based on image repeat value
            last_number = self.__last_frames[0] if len(self.__last_frames) > 0 else len(self.__existing_images)
            if ((repeated == False and last_frame_counter >= last_number) or
                    (repeated and last_frame_counter == len(self.__existing_images))):

                if len(self.__last_frames) > 0:
                    l_frames.append(last_frame_counter) if last_frame_counter == len(self.__existing_images) \
                        else l_frames.append(last_frame_counter - 1)
                    self.__last_frames.pop(0)
                else:
                    l_frames[-1] = last_frame_counter if last_frame_counter == len(self.__existing_images) \
                        else last_frame_counter - 1

            last_frame_counter += 1
        self.__last_frames = l_frames
        print(
            f'{len(self.__unique_images)} unique images found \n {len(self.__removed_images)} duplicate images removed')

    def __images_different(self):
        """
        Check if two images are different based on color, histogram, and noise.

        This method uses two internal methods, __detect_noise_and_artifacts() and __compare_histogram(),
        to analyze and compare the images. If either of these methods indicates that the images are different,
        this method returns True. Otherwise, it returns False.

        Returns:
        - bool: True if the images are different, False otherwise.
        """
        try:

            if self.__detect_noise_and_artifacts() or self.__compare_histogram():
                # Image is different
                return True

        except Exception as e:
            print(f'Unable to differentiate images : {e}')
            return True
        # Image is same
        return False

    def __update_json_file(self):
        """
        Update the 'frames' field in the JSON file with the names of unique images and also update their lastFrame value

        This method reads the existing JSON file, adds or updates the 'frames' field
        with the names of unique images, and writes the modified data back to the file.

        The JSON file is expected to have a list of entries, and each entry may contain
        other fields in addition to or excluding the 'frames' field.

        Note:
        - The 'frames' field is updated for each entry in the JSON file.
        - The 'lastFrame' field is updated for each entry in the JSON file.
        """
        try:
            print(f'Updating json file')
            json_file_path = os.path.join(self.__filmstrip_directory, self.__json_file)
            with open(json_file_path, 'r+') as file:
                data = json.load(file)

                # Modify the data by adding the "frames" field
                for i, entry in enumerate(data):
                    entry["frames"] = self.__unique_images
                    entry["lastFrame"] = self.__last_frames[i]

                # Seek to the beginning of the file for writing
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()  # Truncate remaining data after the write
        except Exception as e:
            print(f'Json file not found {e}')

    def configure_image_timestamp(self, png=None, timestamp=None):
        """
        Configure and add timestamps to images based on their uniqueness in the collection.

        This method iterates through the images in the timestamp dictionary (__timestamp_images)
        and adds a formatted timestamp to each image.

        The timestamp is extracted and converted to the format "YYYY-MM-DD HH:MM:SS.sss". It is then appended to the
        image

        Parameters:
        - png (str): The filename of the image to which the timestamp will be added.
        - timestamp (float): The original timestamp in milliseconds.

        Note:
        - Timestamps are added using the __add_timestamp method.
        - The time series range is included in the timestamp label for grouped images.

        Examples:
        - To add a timestamp to a single image:
          configure_image_timestamp(png='example_image.png', timestamp=1646098752000)

        - To add timestamps for a series of images in a time series:
          configure_image_timestamp()

        """
        try:
            if png and timestamp:
                timestamp = datetime.datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                self.__add_timestamp(png, f'Screenshot @ {timestamp} UTC    ', filmstrip=False)
            else:
                image_same = False
                time_series_start = None
                for img, timestamp in self.__timestamp_images.items():
                    timestamp = datetime.datetime.utcfromtimestamp(timestamp / 1000.0).strftime(
                        "%Y-%m-%d %H:%M:%S.%f")[:-3]
                    if img in self.__unique_images:
                        # directly add timestamp
                        if image_same:
                            timestamp = f'{time_series_start} - {timestamp}'
                            image_same = False
                        self.__add_timestamp(img, f'Filmstrip @ {timestamp} UTC ', filmstrip=True)
                    else:
                        if not image_same:
                            image_same = True
                            time_series_start = timestamp
        except Exception as e:
            print('Error while configuring timestamps')

    def __add_timestamp(self, image, timestamp, filmstrip=False):
        """
        Add a timestamp to the specified image.

        This method reads the image, adds a timestamp using OpenCV, and saves the modified image.

        Parameters:
        - image (str): The filename of the image to which the timestamp will be added.
        - timestamp (str): The timestamp to be added to the image.
        - filmstrip (bool, optional): Indicates whether the image belongs to a filmstrip. Default is False.

        Note:
        - The timestamp is added to the bottom-right corner of the image, or adjusted to the center
          if it goes beyond image boundaries.

        Examples:
        - To add a timestamp to a regular image:
          __add_timestamp(image='example_image.png', timestamp='2022-02-29 12:34:56')

        - To add a timestamp to an image within a filmstrip:
          __add_timestamp(image='filmstrip_image.png', timestamp='Filmstrip @ 2022-02-29 12:34:56 UTC', filmstrip=True)
        """
        try:
            image_path = f'{os.path.join(self.__filmstrip_directory, image)}' if filmstrip else \
                f'{os.path.join(self.__directory, image)}'
            image = cv2.imread(image_path)

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5

            # Choose the font color, thickness, and line type
            font_color = self.__configure_font_color(image_path)
            font_thickness = 1
            line_type = cv2.LINE_AA

            # if mobile images detected
            if self.__mobile_emulator:
                if filmstrip:
                    font_scale *= 0.6
                else:
                    font_scale += 0.4
                # rotate image anticlockwise to insert and fit whole timestamp
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

            if self.__screenshot_text_size is None and filmstrip == False:
                self.__screenshot_text_size = \
                    cv2.getTextSize(self.__sample_ss_timestamp, font, font_scale, font_thickness)[0]

            elif self.__filmstrip_text_size is None and filmstrip:
                self.__filmstrip_text_size = \
                    cv2.getTextSize(self.__sample_fs_timestamp, font, font_scale, font_thickness)[0]

            # Calculate the text size to position it properly
            text_size = self.__filmstrip_text_size if filmstrip else self.__screenshot_text_size

            if filmstrip and self.__fs_position is None:
                self.__fs_position = self.__configure_position(image, text_size, filmstrip)
            elif filmstrip == False and self.__ss_position is None:
                self.__ss_position = self.__configure_position(image, text_size, filmstrip)

            position = self.__fs_position if filmstrip else self.__ss_position

            # Add the timestamp to the image
            cv2.putText(image, timestamp, position, font, font_scale, font_color, font_thickness, line_type)

            # rotate mobile image back to its original state
            if self.__mobile_emulator:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

            # Save the modified image
            cv2.imwrite(image_path, image)
        except Exception as e:
            print(f'Error while inserting timestamp {e}')

    def __configure_position(self, image, text_size, filmstrip):
        position = [image.shape[1] - text_size[0], image.shape[0] - text_size[1]]
        if self.__mobile_emulator and filmstrip:
            position[1] -= 10

        # Check if the position is within the image boundaries
        if (position[0] < 0 or position[1] < 0 or position[0] + text_size[0] > image.shape[1] or position[1] -
                text_size[1] < 0):
            print("Warning: Text is outside image boundaries. Adjusting to center of image ")
            # Calculate the position to center the text at the bottom of the image
            position = ((image.shape[1] - text_size[0]) // 2, (image.shape[0] + text_size[1]) // 2)

        return position

    @staticmethod
    def __configure_font_color(image_path):
        """
        This function extracts the most dominant color from an image and returns both the dominant color
        and its inverted version.

        Args:
            image_path (str): Path to the image file.

        Returns:
            tuple: A tuple containing the following:

                - inverted_color (tuple): The inverted color in RGB format (R, G, B).

        """

        try:

            # Open the image and get pixel data (faster than iterating pixels)
            img = Image.open(image_path).convert('RGB').getdata()

            # Use Counter for efficient color counting
            color_counts = Counter(img)

            # Find dominant color using most_common (faster than max + key)
            dominant_color = color_counts.most_common(1)[0][0]  # Get first element (color)

            # Invert dominant color (same as before)
            inverted_color = tuple(255 - value for value in dominant_color)

            return inverted_color

        except (IOError, OSError) as e:
            print(f"Could not open image file: {image_path}. Error: {e}")
            return 127, 0, 127

    def start_process(self, filmstrip_active, screenshot_active, session_id, screenshot_timestamps):
        """
        Start the process of comparing images for a given session.

        This method fetches image names using the provided session ID, processes two images,
        configures their timestamps, and updates the associated JSON file.

        Parameters:
        - filmstrip_active (bool): Indicates whether filmstrip processing is active.
        - screenshot_active (bool): Indicates whether screenshot processing is active.
        - session_id (str): A unique identifier for the session, used to fetch images
          and update the JSON file.
        - screenshot_timestamps (dict): A dictionary containing image filenames as keys
          and their corresponding timestamps as values.

        Note:
        - The method checks for the active status of filmstrip and screenshot processing
          before initiating the process.

        Examples:
        - To start processing screenshots for a session with ID '123' and provided timestamps:
          start_process(filmstrip_active=False, screenshot_active=True, session_id='123',
                        screenshot_timestamps={'image1.png': 1646098752000, 'image2.png': 1646098760000})

        - To start processing filmstrip for a session with ID '456':
          start_process(filmstrip_active=True, screenshot_active=False, session_id='456', screenshot_timestamps={})
        """
        if screenshot_active and len(screenshot_timestamps) > 0:
            print('Processing screenshots')
            for png, timestamps in screenshot_timestamps.items():
                self.configure_image_timestamp(png, timestamps)
        if filmstrip_active and session_id is not None:
            print('Processing filmstrip')
            self.__fetch_image_names(session_id)
            self.__process_two_images()
            self.configure_image_timestamp()
            self.__update_json_file()

    # For local test and debugging purpose
    def __display_difference(self, img1_path, img2_path):
        """
        Display and save the difference between two images.

        Parameters:
        - img1_path (str): Path to the first image.
        - img2_path (str): Path to the second image.
        """
        image1 = self.__first_image
        image2 = self.__second_image
        difference = cv2.subtract(image1, image2)

        # color the mask red
        conv_hsv_gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(conv_hsv_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        difference[mask != 255] = [0, 0, 255]

        # add the red mask to the images to make the differences obvious
        image1[mask != 255] = [0, 0, 255]
        image2[mask != 255] = [0, 0, 255]

        # store images
        directory = os.path.join(os.getcwd(), 'image_difference')
        cv2.imwrite(f'{directory}/{img1_path.replace(".jpg", "")}_{img2_path.replace(".jpg", "")}.png', difference)

    # For local test and debugging purpose
    def __copy_files(self, destination, image_name):
        """
        Copy unique images to the destination directory and update the associated JSON file.
        """
        # Modify the json file which exists for this session_id
        # Create the destination directory if it doesn't exist
        if isinstance(image_name, list):
            if not os.path.exists(destination):
                os.makedirs(destination)

            # Move unique images to the destination directory
            for image_name in self.__unique_images:
                source_path = os.path.join(self.__filmstrip_directory, image_name)
                destination_path = os.path.join(destination, image_name)
                with open(source_path, 'rb') as source_file, open(destination_path, 'wb') as destination_file:
                    destination_file.write(source_file.read())
        else:
            if not os.path.exists(destination):
                os.makedirs(destination)

            # Move removed images to the destination directory
            source_path = os.path.join(self.__filmstrip_directory, image_name)
            destination_path = os.path.join(destination, image_name)
            with open(source_path, 'rb') as source_file, open(destination_path, 'wb') as destination_file:
                destination_file.write(source_file.read())

    def cleanup(self):
        """
        Release resources held by the CompareFilmstrip object.

        This method closes any open files and clears data structures used by the object.

        Note:
        - If the JSON file is open, it will be closed.
        - Data structures (__existing_images, __removed_images, __unique_images, __timestamp_images)
          are cleared.
        - Images are cleared
        """
        # Close any open files
        if self.__json:
            try:
                self.__json.close()
            except:
                pass  # File already closed

        # Clear data structures
        self.__existing_images.clear()
        self.__removed_images.clear()
        self.__unique_images.clear()
        self.__timestamp_images.clear()
        self.__last_frames = None
        self.__first_image = None
        self.__second_image = None
        self.__tmp_image = None
        self.__fs_position = None
        self.__screenshot_text_size = None
        self.__filmstrip_text_size = None
        self.__ss_position = None
