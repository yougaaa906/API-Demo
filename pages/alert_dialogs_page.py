from pages.basepage import BasePage
from pages.page_actions import PageActions
import logging
from appium.webdriver.common.appiumby import AppiumBy  # Use AppiumBy for mobile best practice
from selenium.webdriver.support import expected_conditions as EC

class AlertDialogsPage(BasePage):
    logger = logging.getLogger(__name__)
    # Use AppiumBy (better adaptation for mobile automation instead of original By)
    app_btn = (AppiumBy.ACCESSIBILITY_ID, "App")
    alert_dialogs_btn = (AppiumBy.ACCESSIBILITY_ID,"Alert Dialogs")
    cancel_dialog_with_a_message_btn = (AppiumBy.ACCESSIBILITY_ID,"OK Cancel dialog with a message")
    alert_title = (AppiumBy.ID,"android:id/alertTitle")
    cancel_btn = (AppiumBy.ID,"android:id/button2") 
    ok_btn = (AppiumBy.ID,"android:id/button1")

    def alert_dialogs_page(self):
        """
        Perform alert dialog operations (click Cancel → click OK to close dialog)
        Verify dialog closure status and return boolean result for assertion in Test layer
        :return: Boolean - True = dialog closed successfully; False = dialog not closed
        """
        try:
            self.logger.info("Starting Alert Dialogs operation flow")
            # Step 1: Navigate to Alert Dialogs page
            self.elem_click(self.app_btn)
            self.elem_click(self.alert_dialogs_btn)
            self.logger.info("Successfully navigated to Alert Dialogs page")

            # Step 2: Click dialog button and wait for alert title to display
            self.elem_click(self.cancel_dialog_with_a_message_btn)
            alert_title_elem = self.wait_elem_visibility(self.alert_title)
            self.logger.info(f"Alert dialog title displayed: {alert_title_elem.text.strip()}")

            # Step 3: Click Cancel button to close dialog
            self.elem_click(self.cancel_btn)
            self.logger.info("Clicked Cancel button to close alert dialog")

            # Step 4: Open dialog again and click OK button to close
            self.elem_click(self.cancel_dialog_with_a_message_btn)
            self.elem_click(self.ok_btn)
            self.logger.info("Clicked OK button to close alert dialog")

            # Step 5: Core validation - Verify if dialog is truly closed (return boolean for Test layer assertion)
            # Wait for alert title to be invisible → confirm dialog closure
            is_alert_closed = self.wait.until(EC.invisibility_of_element_located(self.alert_title))
            self.logger.info(f"Alert dialog closure status: {is_alert_closed}")

            return is_alert_closed  # Return boolean (True = closed successfully, False = not closed)

        except Exception as e:
            self.logger.error(f"Alert dialog operation failed, error: {str(e)}")
            raise e
