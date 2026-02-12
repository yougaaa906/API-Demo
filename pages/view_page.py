from pages.basepage import BasePage
from pages.page_actions import PageActions
import logging
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy


class ViewPage(BasePage):
    logger = logging.getLogger(__name__)
    view_btn = (AppiumBy.ACCESSIBILITY_ID,"Views")
    chronometer_btn = (AppiumBy.ACCESSIBILITY_ID,"Chronometer")



    def view_page(self):
        try:
            swipe_actions = PageActions(self.driver)
            swipe_actions.swipe_until_element_appear(locator=self.view_btn)
            self.logger.info("往上滑动已找到元素")
            self.elem_click(self.view_btn)
            chronometer_btn_elem = self.wait_elem_visibility(self.chronometer_btn)
            self.logger.info("页面跳转成功")
            return chronometer_btn_elem.text.strip()
        except Exception as e:
            self.logger.info(f"页面跳转失败，失败原因是：{str(e)}")
            raise e


