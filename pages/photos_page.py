# ========== Full Imports at Top ==========
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
import logging
from pages.basepage import BasePage
from config.config import TIMEOUT  

# Global logger (accessible both inside and outside class to avoid attribute errors)
logger = logging.getLogger(__name__)

# ========== Class Definition (All attributes are class-level with correct indentation) ==========
class PhotosPage(BasePage):
    # Class-level attributes: Same indentation as __init__, accessible by all instances
    # Photos entry in Views page
    gallery_btn = (AppiumBy.ACCESSIBILITY_ID, "Gallery")
    photos_btn = (AppiumBy.ACCESSIBILITY_ID, "1. Photos")

    # Image container (base element for swiping)
    PHOTO_CONTAINER = (AppiumBy.ID, "io.appium.android.apis:id/gallery")

    def photos_page(self):
        """
        Navigate to Photos scene (no attribute errors)
        :raise: NoSuchElementException if Gallery/Photos button not found
        """
        try:
            self.elem_click(self.gallery_btn)
            self.elem_click(self.photos_btn)
            logger.info("Successfully navigated to Photos scene")
            self.driver.implicitly_wait(TIMEOUT)  
            logger.info(f"Set implicit wait time to {TIMEOUT} seconds for page stabilization")
        except NoSuchElementException as e:
            logger.error(f"Failed to navigate to Photos scene: {str(e)}")
            raise e

    def swipe_to_last_photo(self, max_swipes=8):
        """
        Swipe left continuously to reach the last photo in the gallery container
        Uses container's size/location to calculate swipe coordinates (device-adaptive)
        :param max_swipes: Maximum swipe attempts to prevent infinite loop (default: 8)
        :return: True - reached last photo; False - max swipes reached without finding last photo
        """
        # 1. Get size and location of the photo container (core logic)
        container = self.driver.find_element(*self.PHOTO_CONTAINER)
        container_width = container.size['width']
        container_x = container.location['x']  # X coordinate of container on screen
        last_x = 0  # Record boundary position after last swipe

        for swipe_count in range(max_swipes):
            # 2. Get rightmost X coordinate of current visible area (boundary check)
            current_right_x = container_x + container_width

            # 3. If current boundary equals last boundary, reach the last photo (no more swipe possible)
            if current_right_x == last_x:
                logger.info(f"Swipe attempt {swipe_count + 1}: Reached the last photo in gallery")
                return True  # Return boolean for assertion

            # 4. Perform left swipe (calculate coordinates using container size - core logic)
            self.driver.swipe(
                start_x=container_x + container_width * 0.9,
                start_y=container.location['y'] + container.size['height'] * 0.5,
                end_x=container_x + container_width * 0.1,
                end_y=container.location['y'] + container.size['height'] * 0.5,
                duration=500
            )

            last_x = current_right_x  # Update last boundary position
            logger.info(f"Swipe attempt {swipe_count + 1}: Performing left swipe to next photo")

        # 5. Max swipes reached without finding last photo
        logger.info(f"Max swipe attempts ({max_swipes}) reached, last photo not found")
        return False
