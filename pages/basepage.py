# Import required libraries
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os
import logging
from config.config import TIMEOUT

class BasePage:
    """Base Page Class: Encapsulates common methods for all page objects (wait, swipe, screenshot)"""
    logger = logging.getLogger(__name__)

    def __init__(self, driver):
        self.driver = driver  # Receive Appium driver instance
        self.wait = WebDriverWait(self.driver, TIMEOUT)  # Explicit wait with global timeout

    # Common Method 1: Wait for element visibility (core method to replace sleep)
    def wait_elem_visibility(self, locator, timeout=None):
        """
        Wait until the element is visible on the screen
        :param locator: Element locator tuple (by, value), e.g., (AppiumBy.XPATH, "//button")
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Visible web element object
        :raise: TimeoutException if element is not visible within timeout
        """
        # Priority: use custom timeout, fallback to global TIMEOUT
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"Waiting for element visibility: {locator}, timeout: {timeout}s")
            elem = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            self.logger.info(f"Element {locator} is visible")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Element {locator} not visible within {timeout}s: {str(e)}")
            raise TimeoutException(f"Element not found: {locator}, error: {str(e)}") from e

    def elem_clickable(self, locator, timeout=None):
        """
        Wait until the element is clickable
        :param locator: Element locator tuple (by, value)
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Clickable web element object
        :raise: TimeoutException if element is not clickable within timeout
        """
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"Waiting for element clickable: {locator}, timeout: {timeout}s")
            elem = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            self.logger.info(f"Element {locator} is clickable")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Element {locator} not clickable within {timeout}s: {str(e)}")
            raise TimeoutException(f"Element {locator} not clickable, error: {str(e)}") from e

    def elem_input(self, locator, text, timeout=None):
        """
        Wait for element visibility then input text
        :param locator: Element locator tuple (by, value)
        :param text: Text to be inputted into the element
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Element object after text input
        :raise: TimeoutException if element is not visible within timeout
        """
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"Inputting text '{text}' to element {locator}")
            elem = self.wait_elem_visibility(locator, timeout)
            elem.clear()  # Clear input field before typing
            elem.send_keys(text)
            self.logger.info(f"Text '{text}' inputted to element {locator} successfully")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Input element {locator} not found within {timeout}s: {str(e)}")
            raise TimeoutException(f"Input element {locator} not found, error: {str(e)}") from e

    def elem_click(self, locator, timeout=None):
        """
        Wait for element clickable then perform click action
        :param locator: Element locator tuple (by, value)
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Element object after click
        :raise: TimeoutException if element is not clickable within timeout
        """
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"Preparing to click element: {locator}")
            elem = self.elem_clickable(locator, timeout)
            elem.click()
            self.logger.info(f"Element {locator} clicked successfully")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Failed to click element {locator}: {str(e)}")
            raise TimeoutException(f"Failed to click element {locator}, error: {str(e)}") from e

    # Deprecated: Use PageActions.swipe_until_element_appear() for element-specific swiping
    # Kept for backward compatibility and basic swipe scenarios
    def swipe_up(self, times=1, duration=1000):
        """
        Perform upward swipe on screen (bottom to top)
        :param times: Number of swipe iterations (default: 1)
        :param duration: Swipe duration in milliseconds (default: 1000ms)
        :raise: Exception if swipe fails after all iterations
        """
        for attempt in range(times):
            # Get screen resolution for swipe coordinates
            screen_size = self.driver.get_window_size()
            start_x = screen_size["width"] / 2  # Start X: middle of screen width
            start_y = screen_size["height"] * 0.8  # Start Y: 80% of screen height (bottom)
            end_y = screen_size["height"] * 0.2  # End Y: 20% of screen height (top)
            
            try:
                # Execute swipe action
                self.driver.swipe(start_x, start_y, start_x, end_y, duration)
                self.logger.info(f"Swipe up attempt {attempt+1}/{times} completed")
                time.sleep(0.5)  # Short pause to avoid too fast operations
            except Exception as e:
                self.logger.warning(f"Swipe up attempt {attempt+1} failed: {str(e)}")
                # Capture screenshot and raise exception on last failed attempt
                if attempt == times - 1:
                    self.screenshot()
                    raise Exception(f"Failed to perform swipe up after {times} attempts: {str(e)}") from e
                continue

    # Deprecated: Use PageActions.swipe_until_element_appear() with direction="left"
    def swipe_left(self):
        """Perform left swipe on screen (right to left) with fixed duration (800ms)"""
        screen_size = self.driver.get_window_size()
        start_x = screen_size["width"] * 0.8  # Start X: 80% of screen width (right)
        start_y = screen_size["height"] / 2   # Start Y: middle of screen height
        end_x = screen_size["width"] * 0.2    # End X: 20% of screen width (left)
        
        try:
            self.driver.swipe(start_x, start_y, end_x, start_y, 800)
            self.logger.info("Swipe left action completed successfully")
        except Exception as e:
            self.logger.error(f"Failed to perform swipe left: {str(e)}")
            self.screenshot()
            raise

    # Common Method 4: Capture screenshot (auto-called on failure)
    def screenshot(self):
        """Capture and save screenshot to screenshots directory with timestamp"""
        # Get project root path for robust directory handling
        project_root = os.path.dirname(os.path.abspath(__file__))
        screenshots_dir = os.path.join(project_root, "screenshots")
        
        # Create directory if not exists
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate unique filename with timestamp to avoid duplication
        filename = f"error_{time.strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join(screenshots_dir, filename)
        
        # Save screenshot and log the path
        self.driver.save_screenshot(screenshot_path)
        self.logger.error(f"Error screenshot saved to: {screenshot_path}")
