from pages.basepage import BasePage
from pages.page_actions import PageActions
import logging
from appium.webdriver.common.appiumby import AppiumBy  # 统一用AppiumBy（移动端最佳实践）
from config.config import INPUT_TEXT


class TextFieldsPage(BasePage):
    logger = logging.getLogger(__name__)
    # ✅ 统一用AppiumBy，替换原生By（仅修复定位策略，不新增逻辑）
    textfields_btn = (AppiumBy.ACCESSIBILITY_ID, "TextFields")
    textfields_page_title = (AppiumBy.XPATH, "//android.widget.TextView[@text='Views/TextFields']")
    textfields_field = (AppiumBy.ID, "io.appium.android.apis:id/edit")

    def textfields_page(self, input_text=INPUT_TEXT):
        try:
            self.logger.info("开始执行TextFields页面输入操作")
            swipe_actions = PageActions(self.driver)

            # 1. 滑动找到目标元素
            swipe_actions.swipe_until_element_appear(locator=self.textfields_btn)
            self.logger.info("往上滑动已找到TextFields按钮")  # ✅ 修复日志调用（补全info）

            # 2. 点击进入页面
            self.elem_click(self.textfields_btn)
            self.logger.info("点击TextFields按钮，等待页面标题显示")

            # 3. 等待页面加载完成
            self.wait_elem_visibility(self.textfields_page_title)

            # 4. 输入文本（仅执行输入，不做验证）
            self.logger.info(f"在输入框中输入文本：{input_text}")
            self.elem_input(self.textfields_field, input_text)

            # 5. 获取输入后文本并返回（精简冗余等待）
            textfields_text = self.driver.find_element(*self.textfields_field).text.strip()
            self.logger.info("输入操作完成，返回输入框文本")

            return textfields_text
        except Exception as e:
            # ✅ 修复日志级别（改为error），规范格式化
            self.logger.error(f"输入操作失败，失败原因：{str(e)}")
            raise e