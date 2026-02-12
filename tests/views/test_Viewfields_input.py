from pages.textfields_page import TextFieldsPage
import logging
import pytest

# 无需手动导入夹具！pytest会自动识别conftest.py中的夹具
# from tests.views.conftest import goto_views_page  ✅ 删掉这行（多余且易出错）

logger = logging.getLogger(__name__)


def test_view_page_jump(goto_views_page):
    """测试TextFields页面文本输入功能（依赖跳转Views页面的夹具）"""
    try:
        logger.info("========输入用例开始执行========")

        # ✅ 优化：直接复用夹具的driver（或ViewPage对象），无需额外取值
        # 方式1：若goto_views_page yield的是driver（原始夹具）
        # input_elem = TextFieldsPage(goto_views_page)
        # 方式2：若goto_views_page yield的是ViewPage对象（推荐的修复版夹具）
        input_elem = TextFieldsPage(goto_views_page.driver)

        # 执行输入操作，获取返回文本
        input_text = input_elem.textfields_page()

        # ✅ 优化：断言提示补充预期/实际值，精准定位问题
        expected_text = "Today is a sunny day!"
        assert expected_text in input_text, \
            f"输入文本验证失败！预期包含：{expected_text}，实际：{input_text}"

        logger.info(f"输入文本成功！输入框内容：{input_text}")

    except AssertionError as ae:
        # ✅ 单独捕获断言失败，日志级别为error
        logger.error(f"输入文本断言失败：{str(ae)}")
        raise ae  # 抛出断言异常，让pytest标记用例失败
    except Exception as e:
        # ✅ 其他异常用error级别，补充堆栈信息（可选）
        logger.error(f"输入文本执行失败，失败原因：{str(e)}", exc_info=True)
        raise e