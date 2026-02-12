from pages.basepage import BasePage
from pages.page_actions import PageActions
import logging
from appium.webdriver.common.appiumby import AppiumBy  # 统一用AppiumBy（移动端最佳实践）
from selenium.webdriver.support import expected_conditions as EC

class AlertDialogsPage(BasePage):
    logger = logging.getLogger(__name__)
    # ✅ 统一用AppiumBy，替换原生By（移动端适配更优）
    app_btn = (AppiumBy.ACCESSIBILITY_ID, "App")
    alert_dialogs_btn = (AppiumBy.ACCESSIBILITY_ID,"Alert Dialogs")
    cancel_dialog_with_a_message_btn = (AppiumBy.ACCESSIBILITY_ID,"OK Cancel dialog with a message")
    alert_title = (AppiumBy.ID,"android:id/alertTitle")
    cancle_btn = (AppiumBy.ID,"android:id/button2")
    ok_btn = (AppiumBy.ID,"android:id/button1")

    def alert_dialogs_page(self):
        """
        执行弹窗操作（点击Cancel→点击OK关闭弹窗），返回：弹窗是否成功关闭（布尔值）
        """
        try:
            self.logger.info("开始执行Alert Dialogs弹窗操作")
            # 1. 进入Alert Dialogs页面
            self.elem_click(self.app_btn)
            self.elem_click(self.alert_dialogs_btn)
            self.logger.info("成功进入Alert Dialogs页面")

            # 2. 点击弹窗按钮，等待弹窗标题显示
            self.elem_click(self.cancel_dialog_with_a_message_btn)
            alert_title_elem = self.wait_elem_visibility(self.alert_title)
            self.logger.info(f"弹窗标题显示：{alert_title_elem.text.strip()}")

            # 3. 点击Cancel按钮
            self.elem_click(self.cancle_btn)
            self.logger.info("点击Cancel按钮关闭弹窗")

            # 4. 再次打开弹窗，点击OK按钮关闭
            self.elem_click(self.cancel_dialog_with_a_message_btn)
            self.elem_click(self.ok_btn)
            self.logger.info("点击OK按钮关闭弹窗")

            # 5. 核心：验证弹窗是否真的关闭（返回布尔值给Test层断言）
            # 等待弹窗标题不可见 → 确认弹窗关闭
            is_alert_closed = self.wait.until(EC.invisibility_of_element_located(self.alert_title))
            self.logger.info(f"弹窗关闭状态：{is_alert_closed}")

            return is_alert_closed  # ✅ 返回布尔值（True=关闭成功，False=未关闭）

        except Exception as e:
            self.logger.error(f"弹窗操作失败，失败原因：{str(e)}")  # ✅ 日志级别改为error
            raise e