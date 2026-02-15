from pages.basepage import BasePage
from pages.page_actions import PageActions
import logging
from appium.webdriver.common.appiumby import AppiumBy  # Use AppiumBy for mobile best practice
from config.config import INPUT_TEXT


class TextFieldsPage(BasePage):
    """TextFields Page Object: Encapsulates elements and actions for TextFields page"""
    logger = logging.getLogger(__name__)
    
    # Page Element Locators (use AppiumBy for mobile automation best practice)
    textfields_btn = (AppiumBy.ACCESSIBILITY_ID, "TextFields")
    textfields_page_title = (AppiumBy.XPATH, "//android.widget.TextView[@text='Views/TextFields']")
    textfields_field = (AppiumBy.ID, "io.appium.android.apis:id/edit")

    def textfields_page(self, input_text=INPUT_TEXT):
        """
        Perform text input operation on TextFields page
        Steps:
        1. Swipe to locate TextFields button
        2. Click button to navigate to TextFields page
        3. Wait for page title to confirm page load
        4. Input text to the target text field
        5. Retrieve and return the inputted text
        :param input_text: Text to be inputted (default: global INPUT_TEXT from config)
        :return: Trimmed text from the input field after input
        :raise: Exception if any step fails during the operation
        """
        try:
            self.logger.info("Starting text input operation on TextFields page")
            swipe_actions = PageActions(self.driver)

            # Step 1: Swipe to find target element
            swipe_actions.swipe_until_element_appear(locator=self.textfields_btn)
            self.logger.info(f"TextFields button ({self.textfields_btn}) found after upward swipe")

            # Step 2: Click to enter TextFields page
            self.elem_click(self.textfields_btn)
            self.logger.info("Clicked TextFields button, waiting for page title to display")

            # Step 3: Wait for page to load completely (verify title visibility)
            self.wait_elem_visibility(self.textfields_page_title)

            # Step 4: Input text (only perform input, no validation)
            self.logger.info(f"Inputting text '{input_text}' to the text field")
            self.elem_input(self.textfields_field, input_text)

            # Step 5: Retrieve inputted text and return (simplify redundant wait)
            textfields_text = self.driver.find_element(*self.textfields_field).text.strip()
            self.logger.info("Text input operation completed, returning text from input field")

            return textfields_text
        except Exception as e:
            self.logger.error(f"Text input operation failed, error: {str(e)}")
            raise e
