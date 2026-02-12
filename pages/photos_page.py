# ========== 顶部完整导入 ==========
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
import logging
from pages.basepage import BasePage

# 全局日志器（类内外均可调用，避免属性错误）
logger = logging.getLogger(__name__)

# ========== 类定义（所有属性均为类级，缩进正确） ==========
class PhotosPage(BasePage):
    # ✅ 类级属性：缩进与__init__同级，所有实例均可访问
    # Views页面的Photos入口
    gallery_btn = (AppiumBy.ACCESSIBILITY_ID,"Gallery")
    photos_btn = (AppiumBy.ACCESSIBILITY_ID, "1. Photos")

    # 图片容器（滑动的基准元素）
    PHOTO_CONTAINER = (AppiumBy.ID, "io.appium.android.apis:id/gallery")



    def photos_page(self):
        """进入Photos场景（无属性错误）"""
        try:
            self.elem_click(self.gallery_btn)
            self.elem_click(self.photos_btn)
            logger.info("✅ 成功进入Photos场景")
            self.driver.implicitly_wait(2)
        except NoSuchElementException as e:
            logger.error(f"❌ 进入Photos场景失败：{str(e)}")
            raise e

    def swipe_to_last_photo(self, max_swipes=8):

        # 1. 获取图片容器的尺寸（你的核心思路）
        container = self.driver.find_element(*self.PHOTO_CONTAINER)
        container_width = container.size['width']
        container_x = container.location['x']  # 容器在屏幕的x坐标
        last_x = 0  # 记录上一次滑动后的边界位置

        for swipe_count in range(max_swipes):
            # 2. 获取当前可见区域的最右侧x坐标（判定边界）
            current_right_x = container_x + container_width

            # 3. 如果当前边界和上一次一致，说明滑不动了（到最后一张）
            if current_right_x == last_x:
                logger.info(f"第{swipe_count + 1}次滑动：已到最后一张图片")
                return True  # 返回布尔值，供断言

            # 4. 左滑动作（用容器尺寸计算坐标，你的核心思路）
            self.driver.swipe(
                start_x=container_x + container_width * 0.9,
                start_y=container.location['y'] + container.size['height'] * 0.5,
                end_x=container_x + container_width * 0.1,
                end_y=container.location['y'] + container.size['height'] * 0.5,
                duration=500
            )

            last_x = current_right_x  # 更新上一次边界位置
            logger.info(f"第{swipe_count + 1}次滑动：继续左滑")

        # 5. 滑完最大次数仍没到最后，返回False
        logger.info(f"滑完{max_swipes}次仍未到最后一张")
        return False
