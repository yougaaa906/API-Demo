import pytest
from pages.view_page import ViewPage
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def goto_views_page(driver):
    logger.info(f"====跳转views页面=======")
    views_page_operations = ViewPage(driver)  # 变量名优化：login_success → login_page（更语义化）
    try:
        views_page_operations.view_page()
        logger.info(f"跳转views页面成功")
        yield views_page_operations
    except Exception as e:
        logger.error(f"跳转views页面失败，失败原因：{str(e)}")  # 改为error级别
        raise e






