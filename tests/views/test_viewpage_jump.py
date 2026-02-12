from pages.view_page import ViewPage
import logging
import pytest

logger = logging.getLogger(__name__)

def test_view_page_jump(driver):
    try:
        logger.info("========页面跳转用例开始执行========")
        jump_operations = ViewPage(driver)
        jump_result = jump_operations.view_page()
        assert "Chronometer" in jump_result,"跳转页面失败"
        logger.info("页面跳转成功")
    except Exception as e:
        logger.info(f"页面跳转失败，失败原因是：{str(e)}")
        raise e
