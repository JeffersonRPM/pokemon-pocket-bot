import time

import cv2
import easyocr
from skimage.metrics import structural_similarity as ssim

from utils.adb_utils import click_position, find_subimage, take_screenshot


class ImageProcessor:
    def __init__(self, log_callback, debug_window=None):
        self.log_callback = log_callback
        self.debug_window = debug_window

    def reset_view(self):
        click_position(0, 1350)
        click_position(0, 1350)

    def get_card(self, x, y, duration=1.0, debug_window=None, debug_message=None):
        x_zoom_card_region, y_zoom_card_region, w, h = (80, 255, 740, 1020)
        from utils.adb_utils import long_press_position

        # Get the screenshot with debug logging
        screenshot = long_press_position(
            x, y, duration, debug_window=debug_window, debug_message=debug_message
        )

        # Crop the relevant region
        card_image = screenshot[
            y_zoom_card_region : y_zoom_card_region + h,
            x_zoom_card_region : x_zoom_card_region + w,
        ]

        return card_image

    def calculate_similarity(self, img1, img2):
        # Check if either image is None or empty
        if img1 is None or img2 is None:
            self.log_callback(
                "Warning: One or both images are None in calculate_similarity"
            )
            return 0

        if img1.size == 0 or img2.size == 0:
            self.log_callback(
                "Warning: One or both images are empty in calculate_similarity"
            )
            return 0

        if img1.shape != img2.shape:
            self.log_callback(
                f"Warning: Image shapes don't match - {img1.shape} vs {img2.shape}"
            )
            return 0

        try:
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            score, _ = ssim(img1_gray, img2_gray, full=True)
            return score
        except cv2.error as e:
            self.log_callback(f"OpenCV error in calculate_similarity: {e}")
            return 0
        except Exception as e:
            self.log_callback(f"Unexpected error in calculate_similarity: {e}")
            return 0

    def extract_number_from_image(self, image):
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(["en"])
        result = reader.readtext(grayscale_image, detail=0)
        numbers = [text for text in result if text.isdigit()]
        return numbers[0] if numbers else None

    def extract_text_from_image(self, image):
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        reader = easyocr.Reader(["en"])
        result = reader.readtext(grayscale_image, detail=0)
        return result

    def capture_region(self, region):
        x, y, w, h = region
        screenshot = take_screenshot()
        if screenshot is None:
            self.log_callback("Failed to capture screenshot in capture_region")
            return None
        return screenshot[y : y + h, x : x + w]

    def check(
        self, screenshot, template_image, log_message=None, similarity_threshold=0.8
    ):
        if screenshot is None:
            self.log_callback("Screenshot is None in check method")
            return False
        _, similarity = find_subimage(screenshot, template_image)
        if log_message:
            log_message = (
                f"{log_message} found - {similarity:.2f}"
                if similarity > similarity_threshold
                else f"{log_message} NOT found - {similarity:.2f}"
            )
            self.log_callback(log_message)
        return similarity > similarity_threshold

    def check_and_click_until_found(
        self,
        template_image,
        log_message,
        running_event,
        similarity_threshold=0.8,
        max_attempts=50,
    ):
        attempts = 0

        self.log_callback(f"Searching... {log_message}")
        while running_event.is_set():
            screenshot = take_screenshot()
            if screenshot is None:
                self.log_callback(
                    "Failed to take screenshot in check_and_click_until_found"
                )
                time.sleep(0.5)
                continue
            position, similarity = find_subimage(screenshot, template_image)

            if similarity > similarity_threshold:
                self.log_and_click(
                    position,
                    f"{log_message} found - {similarity:.2f}",
                    screenshot=screenshot,
                )
                self.log_callback(f"✅ {log_message} found")
                return True
            else:
                attempts += 1
                if attempts >= max_attempts:
                    self.log_callback(
                        f"❌ Max attempts reached. {log_message} not found. Stopping the bot."
                    )
                    return False
                time.sleep(0.5)

    def check_and_click(
        self, screenshot, template_image, log_message=None, similarity_threshold=0.8
    ):
        if screenshot is None:
            self.log_callback("Screenshot is None in check_and_click")
            return False
        position, similarity = find_subimage(screenshot, template_image)
        if similarity > similarity_threshold:
            if log_message:
                self.log_and_click(
                    position,
                    f"{log_message} found - {similarity:.2f}",
                    screenshot=screenshot,
                )
            return True
        else:
            if log_message:
                self.log_callback(f"{log_message} NOT found - {similarity:.2f}")
            return False

    def log_and_click(self, position, message, screenshot=None):
        self.log_callback(message)
        debug_window = (
            self.debug_window
            if (self.debug_window and self.debug_window.is_open)
            else None
        )
        click_position(
            position[0],
            position[1],
            debug_window=debug_window,
            screenshot=screenshot,
        )
