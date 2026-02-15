from pages.photos_page import PhotosPage
import logging
import pytest

logger = logging.getLogger(__name__)

def test_photos_swipe(goto_views_page):
    """
    Test left swipe operation to reach the last photo in Photos gallery
    Uses goto_views_page fixture to pre-navigate to Views page (test isolation)
    Core validation: Verify swipe operation successfully reaches the last photo
    :param goto_views_page: Fixture to navigate to Views page (provides driver via ViewPage object)
    :raise: Exception if test fails (navigation/swipe/assertion error)
    """
    try:
        logger.info("===== Starting Photos gallery swipe test =====")
        # Get Appium driver from the pre-initialized Views page fixture (test isolation)
        driver = goto_views_page.driver
        photos_page = PhotosPage(driver)

        # Execute core operations: Navigate to Photos scene
        photos_page.photos_page()
        # Call page layer method to swipe to last photo (returns boolean result)
        is_last_photo = photos_page.swipe_to_last_photo(max_swipes=8)

        # Core assertion: Verify swipe reached the last photo (main test validation)
        assert is_last_photo is True, f"Failed to swipe to last photo, returned value: {is_last_photo}"
        logger.info("===== Photos gallery swipe test passed =====")

    except Exception as e:
        logger.error(f"Photos gallery swipe test failed: {str(e)}")
        raise e
