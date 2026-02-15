from pages.textfields_page import TextFieldsPage
import logging
import pytest

# pytest automatically detects fixtures from conftest.py - no manual import needed
logger = logging.getLogger(__name__)

def test_textfields_input(goto_views_page):
    """
    Test text input functionality on TextFields page (depends on goto_views_page fixture)
    Core validation: Verify input text is successfully entered and matches expected value
    :param goto_views_page: Fixture to navigate to Views page (provides driver via ViewPage object)
    :raise: AssertionError - if input text verification fails
    :raise: Exception - if other execution errors occur
    """
    try:
        logger.info("======= Starting TextFields input test =======")

        # Optimized: Reuse driver from fixture (ViewPage object) to initialize TextFieldsPage
        text_fields_page = TextFieldsPage(goto_views_page.driver)

        # Execute text input operation and retrieve entered text
        input_result = text_fields_page.textfields_page()

        # Core assertion: Verify input text contains expected value (precise failure debugging)
        expected_text = "Today is a sunny day!"
        assert expected_text in input_result, \
            f"Text input verification failed! Expected to contain: {expected_text}, Actual: {input_result}"

        logger.info(f"Text input test passed! Text field content: {input_result}")

    except AssertionError as ae:
        # Catch assertion failures separately for clear error logging
        logger.error(f"Text input assertion failed: {str(ae)}")
        raise ae  # Re-raise to mark test as failed in pytest
    except Exception as e:
        # Log other exceptions with error level and stack trace for debugging
        logger.error(f"Text input test execution failed, error: {str(e)}", exc_info=True)
        raise e
