# 导入依赖
from pages.alert_dialogs_page import AlertDialogsPage
import logging
import pytest

# 初始化日志器（配置已在conftest.py中统一管理）
logger = logging.getLogger(__name__)



def test_alert_dialogs_close(driver):

    try:
        # 1. 用例开始日志
        logger.info("=====Alert Dialogs弹窗关闭用例开始执行=====")

        # 2. 初始化Page层对象，调用核心操作方法
        alert_page = AlertDialogsPage(driver)
        # 获取Page层返回的弹窗关闭状态（布尔值）
        is_alert_closed = alert_page.alert_dialogs_page()

        # 3. Test层核心断言：验证弹窗是否成功关闭
        assert is_alert_closed is True, f"弹窗关闭验证失败！预期：True（关闭成功），实际：{is_alert_closed}"

        # 4. 用例成功日志
        logger.info("=====Alert Dialogs弹窗关闭用例执行成功=====")

    except AssertionError as ae:
        # 断言失败单独捕获，便于定位问题
        logger.error(f"用例断言失败：{str(ae)}")
        raise ae  # 抛出异常，让pytest标记用例失败
    except Exception as e:
        # 其他异常捕获
        logger.error(f"用例执行异常，失败原因：{str(e)}", exc_info=True)  # 输出完整堆栈，便于调试
        raise e  # 抛出异常，不掩盖错误


