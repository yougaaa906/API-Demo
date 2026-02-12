# 导入需要的库（不用管含义，复制就行）
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import os
import logging
from config.config import TIMEOUT
from selenium.common.exceptions import TimeoutException

class BasePage:
    """基础页面类，封装所有页面通用的方法（等待、滑动、截图）"""
    logger = logging.getLogger(__name__)

    def __init__(self, driver):
        self.driver = driver  # 接收Appium驱动
        self.wait = WebDriverWait(self.driver, 10)  # 显式等待，最多等10秒

    # 通用方法1：等待元素出现（核心，替代sleep）
    def wait_elem_visibility(self, locator, timeout=None):
        """
        等待元素可见
        :param locator: 元素定位器，格式为(定位方式, 定位值)，如(AppiumBy.XPATH, "xxx")
        :param timeout: 超时时间，默认用全局TIMEOUT
        :return: 可见的元素对象
        :raise: TimeoutException 元素超时未可见
        """
        # 修正：优先用传入的timeout，无则用全局TIMEOUT
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"等待元素可见：{locator}，超时{timeout}秒")
            elem = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            self.logger.info(f"元素{locator}已可见")
            return elem
        except TimeoutException as e:
            self.logger.error(f"元素{locator}超时{timeout}秒仍未可见，错误：{str(e)}")
            raise TimeoutException(f"元素没有出现：{locator},错误原因：{str(e)}") from e

    def elem_clickable(self, locator, timeout=None):
        """
        等待元素可点击
        :param locator: 元素定位器
        :param timeout: 超时时间
        :return: 可点击的元素对象
        :raise: TimeoutException 元素超时不可点击
        """
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"等待元素可点击：{locator}，超时{timeout}秒")
            elem = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            self.logger.info(f"元素{locator}已可点击")
            return elem
        except TimeoutException as e:
            self.logger.error(f"元素{locator}超时{timeout}秒仍不可点击，错误：{str(e)}")
            raise TimeoutException(f"{locator}元素不可点击,错误原因：{str(e)}") from e

    def elem_input(self, locator, text, timeout=None):
        """
        等待元素可见后输入文本
        :param locator: 元素定位器
        :param text: 要输入的文本
        :param timeout: 超时时间
        :return: 输入后的元素对象
        :raise: TimeoutException 元素超时未可见
        """
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"向元素{locator}输入文本：{text}")
            elem = self.wait_elem_visibility(locator, timeout)
            elem.clear()  # 清空输入框
            elem.send_keys(text)
            self.logger.info(f"文本{text}已输入到元素{locator}")
            return elem
        except TimeoutException as e:
            self.logger.error(f"输入框元素{locator}超时{timeout}秒未找到，错误：{str(e)}")
            raise TimeoutException(f"输入框元素{locator}没有找到，错误原因：{str(e)}") from e

    def elem_click(self, locator, timeout=None):
        """
        等待元素可点击后点击
        :param locator: 元素定位器
        :param timeout: 超时时间
        :return: 点击后的元素对象
        :raise: TimeoutException 元素超时不可点击
        """
        timeout = timeout or TIMEOUT
        try:
            self.logger.info(f"准备点击元素：{locator}")
            elem = self.elem_clickable(locator, timeout)
            elem.click()
            self.logger.info(f"元素{locator}已点击成功")
            return elem
        except TimeoutException as e:
            self.logger.error(f"点击元素{locator}失败，错误：{str(e)}")
            raise TimeoutException(f"点击元素{locator}没有找到，错误原因：{str(e)}") from e

    # 通用方法2：上下滑动（从下往上滑，自动化最常用）
    def swipe_up(self, times=1, duration=1000):
        # times：滑动次数；duration：滑动时长（毫秒）
        for _ in range(times):
            # 获取屏幕尺寸
            screen_size = self.driver.get_window_size()
            start_x = screen_size["width"] / 2  # 起始x坐标（屏幕中间）
            start_y = screen_size["height"] * 0.8  # 起始y坐标（屏幕下方）
            end_y = screen_size["height"] * 0.2  # 结束y坐标（屏幕上方）
            try:
                # 执行滑动
                self.driver.swipe(start_x, start_y, start_x, end_y, duration)
                time.sleep(0.5)  # 滑完等0.5秒，避免太快
            except:
                # 滑动失败就重试，最后一次失败就截图+报错
                if _ == times - 1:
                    self.screenshot()
                    raise Exception("滑动操作失败了")
                continue

    # 通用方法3：左右滑动（从右往左滑）
    def swipe_left(self):
        screen_size = self.driver.get_window_size()
        start_x = screen_size["width"] * 0.8  # 起始x（屏幕右侧）
        start_y = screen_size["height"] / 2   # 起始y（屏幕中间）
        end_x = screen_size["width"] * 0.2    # 结束x（屏幕左侧）
        self.driver.swipe(start_x, start_y, end_x, start_y, 800)

    # 通用方法4：截图（失败时自动调用）
    def screenshot(self):
        # 新建screenshots文件夹（没有就创建）
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        # 截图文件名（带时间，避免重名）
        filename = f"screenshots/error_{time.strftime('%Y%m%d_%H%M%S')}.png"
        # 保存截图
        self.driver.save_screenshot(filename)
        print(f"错误截图已保存到：{filename}")