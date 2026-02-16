from appium.webdriver import Remote
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

# Get logger instance only (configuration managed in conftest.py)
logger = logging.getLogger(__name__)

class PageActions:
    def __init__(self, driver: Remote):
        self.driver = driver
        # Add explicit wait object (critical fix for WebElement encapsulation)
        self.wait = WebDriverWait(self.driver, 1)  # Short timeout for element check

    # Swipe action (scenario-based extended operation)
    def swipe_until_element_appear(
            self,
            locator,
            max_swipes=10,
            swipe_direction="up",
            swipe_duration=500,
            wait_time=0.5
    ):
        """
        Continuously swipe screen until target element appears (core swipe function)
        Fix: Use WebDriverWait to ensure return WebElement instead of raw dict
        :param locator: Element locator tuple, e.g., (AppiumBy.ID, "com.example.app:id/target_id")
        :param max_swipes: Maximum swipe attempts to prevent infinite loop (default: 10)
        :param swipe_direction: Swipe direction, supports up/down/left/right (default: up)
        :param swipe_duration: Swipe duration in milliseconds (default: 500ms)
        :param wait_time: Wait time after each swipe for page loading (default: 0.5s)
        :return: Found WebElement object / None if element not found
        """
        # Get screen resolution for device adaptation
        screen_size = self.driver.get_window_size()
        width = screen_size["width"]
        height = screen_size["height"]

        swipe_count = 0
        while swipe_count < max_swipes:
            try:
                # CRITICAL FIX: Use WebDriverWait to get encapsulated WebElement
                # Replace direct find_element with explicit wait (solves dict issue)
                element = self.wait.until(
                    EC.visibility_of_element_located(locator)
                )
                # ==========================================================
                from appium.webdriver.webelement import WebElement
                if isinstance(element, dict) and "element-6066-11e4-a52e-28c025000000" in element:
                    element = WebElement(self.driver, element["element-6066-11e4-a52e-28c025000000"])
                # ==========================================================
                logger.info(f"Target element found after {swipe_count} swipes")
                return element
            
            except TimeoutException:  # Replace NoSuchElementException with TimeoutException
                # Execute swipe if element not found
                # Calculate swipe coordinates based on direction
                if swipe_direction == "up":  # Swipe up (page scrolls down)
                    start_x, start_y = width / 2, height * 0.8
                    end_x, end_y = width / 2, height * 0.2
                elif swipe_direction == "down":  # Swipe down (page scrolls up)
                    start_x, start_y = width / 2, height * 0.2
                    end_x, end_y = width / 2, height * 0.8
                elif swipe_direction == "left":  # Swipe left
                    start_x, start_y = width * 0.8, height / 2
                    end_x, end_y = width * 0.2, height / 2
                elif swipe_direction == "right":  # Swipe right
                    start_x, start_y = width * 0.2, height / 2
                    end_x, end_y = width * 0.8, height / 2
                else:
                    logger.error("Invalid swipe direction, only up/down/left/right are supported")
                    return None

                # Perform swipe action (Appium 2.0 compatible)
                self.driver.swipe(start_x, start_y, end_x, end_y, swipe_duration)
                swipe_count += 1
                logger.info(f"Swipe attempt {swipe_count}/{max_swipes} (direction: {swipe_direction})")
                time.sleep(wait_time)  # Wait for page response after swipe

        # Element not found after maximum swipe attempts
        logger.warning(f"Target element not found after {max_swipes} swipe attempts")
        return None
