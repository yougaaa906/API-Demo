# Import dependencies
from pages.alert_dialogs_page import AlertDialogsPage
import logging
import pytest

# Initialize logger (configuration managed centrally in conftest.py)
logger = logging.getLogger(__name__)

def test_alert_dialogs_close(driver):
    """
    Test alert dialog closure functionality (no dependency on Views fixture)
    Core validation: Verify alert dialog is successfully closed after Cancel/OK button clicks
    :param driver: Appium driver fixture from root conftest.py
    :raise: AssertionError - if dialog closure verification fails
    :raise: Exception - if other execution errors occur
    """
    try:
        # Step 1: Log test start
        logger.info("===== Starting Alert Dialogs closure test =====")

        # Step 2: Initialize Page object and execute core operations
        alert_page = AlertDialogsPage(driver)
        # Get dialog closure status (boolean) returned from Page layer
        is_alert_closed = alert_page.alert_dialogs_page()

        # Step 3: Core assertion (Test layer): Verify dialog is closed successfully
        assert is_alert_closed is True, f"Dialog closure verification failed! Expected: True (closed), Actual: {is_alert_closed}"

        # Step 4: Log test success
        logger.info("===== Alert Dialogs closure test passed =====")

    except AssertionError as ae:
        # Catch assertion failures separately for precise debugging
        logger.error(f"Test assertion failed: {str(ae)}")
        raise ae  # Re-raise to mark test as failed in pytest
    except Exception as e:
        # Catch other exceptions with full stack trace for debugging
        logger.error(f"Test execution failed, error: {str(e)}", exc_info=True)
        raise e  # Re-raise to avoid hiding errors
