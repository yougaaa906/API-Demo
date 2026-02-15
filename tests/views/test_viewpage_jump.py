from pages.view_page import ViewPage
import logging
import pytest

logger = logging.getLogger(__name__)

def test_view_page_jump(driver):
    """
    Test navigation to Views page and verify Chronometer button text is displayed
    Core validation: Ensure "Chronometer" is present in the returned text to confirm successful navigation
    :param driver: Appium driver fixture from conftest.py
    :raise: Exception if test fails (navigation/assertion error)
    """
    try:
        logger.info("======= Starting Views page navigation test =======")
        # Initialize ViewPage object to perform navigation operations
        view_page = ViewPage(driver)
        # Execute navigation and get returned text from Chronometer button
        navigation_result = view_page.view_page()
        
        # Core assertion: Verify successful navigation by checking Chronometer text presence
        assert "Chronometer" in navigation_result, "Views page navigation failed - 'Chronometer' not found in result"
        logger.info("Views page navigation test passed: 'Chronometer' text verified")
        
    except Exception as e:
        logger.error(f"Views page navigation test failed, error: {str(e)}")
        raise e
