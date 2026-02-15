import pytest
from pages.view_page import ViewPage
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def goto_views_page(driver):
    """
    Function-scoped fixture to navigate to Views page before test execution
    Yields initialized ViewPage object for test use, ensures navigation success
    :param driver: Appium driver fixture from root conftest.py
    :yield: Initialized ViewPage object
    :raise: Exception if navigation to Views page fails
    """
    logger.info("===== Navigating to Views page =====")
    # Initialize ViewPage object with Appium driver
    view_page = ViewPage(driver)
    try:
        # Execute navigation to Views page
        view_page.view_page()
        logger.info("Successfully navigated to Views page")
        yield view_page
    except Exception as e:
        logger.error(f"Failed to navigate to Views page, error: {str(e)}")
        raise e
