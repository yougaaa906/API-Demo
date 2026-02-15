from pages.basepage import BasePage
from pages.page_actions import PageActions
import logging
from appium.webdriver.common.appiumby import AppiumBy


class ViewPage(BasePage):
    """View Page Object: Encapsulates elements and actions for the Views page"""
    logger = logging.getLogger(__name__)
    
    # Page Element Locators
    view_btn = (AppiumBy.ACCESSIBILITY_ID, "Views")
    chronometer_btn = (AppiumBy.ACCESSIBILITY_ID, "Chronometer")

    def view_page(self):
        """
        Navigate to Views page and get Chronometer button text
        Steps:
        1. Swipe to find Views button
        2. Click Views button to navigate
        3. Wait for Chronometer button to be visible
        4. Return trimmed text of Chronometer button
        :return: Trimmed text of Chronometer button
        :raise: Exception if any step fails during navigation
        """
        try:
            # Initialize swipe action handler
            swipe_actions = PageActions(self.driver)
            
            # Swipe up until Views button appears
            swipe_actions.swipe_until_element_appear(locator=self.view_btn)
            self.logger.info(f"Views button ({self.view_btn}) found after upward swipe")
            
            # Click Views button to navigate to target page
            self.elem_click(self.view_btn)
            
            # Wait for Chronometer button to be visible and get its text
            chronometer_btn_elem = self.wait_elem_visibility(self.chronometer_btn)
            self.logger.info("Successfully navigated to Views page, Chronometer button is visible")
            
            return chronometer_btn_elem.text.strip()
        
        except Exception as e:
            self.logger.error(f"Failed to navigate to Views page, error: {str(e)}")
            raise e
