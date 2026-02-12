from appium.webdriver import Remote
from selenium.common.exceptions import NoSuchElementException
import time
import logging

# 仅获取日志器，不做配置（配置在conftest.py中统一管理）
logger = logging.getLogger(__name__)

class PageActions:
    def __init__(self, driver: Remote):
        self.driver = driver

    # 滑动操作（场景化扩展操作）
    def swipe_until_element_appear(
            self,
            locator,
            max_swipes=10,
            swipe_direction="up",
            swipe_duration=500,
            wait_time=0.5
    ):
        """
        持续滑动直到目标元素出现（核心滑动操作函数）
        :param locator: 元素定位器，如 (AppiumBy.ID, "com.example.app:id/target_id")
        :param max_swipes: 最大滑动次数（防止无限循环）
        :param swipe_direction: 滑动方向，支持 up/down/left/right
        :param swipe_duration: 滑动时长（毫秒）
        :param wait_time: 滑动后等待页面加载的时间（秒）
        :return: 找到的元素对象 / None
        """
        # 获取屏幕尺寸（适配不同设备）
        screen_size = self.driver.get_window_size()
        width = screen_size["width"]
        height = screen_size["height"]

        swipe_count = 0
        while swipe_count < max_swipes:
            try:
                # 检查元素是否存在且可见
                element = self.driver.find_element(*locator)
                if element.is_displayed():
                    logger.info(f"滑动{swipe_count}次后找到目标元素")
                    return element
            except NoSuchElementException:
                # 元素未找到，执行滑动
                # 按方向计算滑动坐标
                if swipe_direction == "up":  # 向上滑（页面向下滚）
                    start_x, start_y = width / 2, height * 0.8
                    end_x, end_y = width / 2, height * 0.2
                elif swipe_direction == "down":  # 向下滑（页面向上滚）
                    start_x, start_y = width / 2, height * 0.2
                    end_x, end_y = width / 2, height * 0.8
                elif swipe_direction == "left":  # 向左滑
                    start_x, start_y = width * 0.8, height / 2
                    end_x, end_y = width * 0.2, height / 2
                elif swipe_direction == "right":  # 向右滑
                    start_x, start_y = width * 0.2, height / 2
                    end_x, end_y = width * 0.8, height / 2
                else:
                    logger.error("滑动方向错误，仅支持 up/down/left/right")
                    return None

                # 执行滑动
                self.driver.swipe(start_x, start_y, end_x, end_y, swipe_duration)
                swipe_count += 1
                logger.info(f"第{swipe_count}次滑动（方向：{swipe_direction}）")
                time.sleep(wait_time)  # 滑动后等待页面响应

        # 达到最大滑动次数仍未找到元素
        logger.warning(f"已滑动{max_swipes}次，未找到目标元素")
        return None