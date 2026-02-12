from pages.photos_page import PhotosPage
import logging
import pytest

logger = logging.getLogger(__name__)

def test_photos_swipe(goto_views_page):
    try:
        logger.info("===== Photos滑动用例开始 =====")
        driver = goto_views_page.driver
        photos_page = PhotosPage(driver)

        # 执行核心操作
        photos_page.photos_page()
        # 调用page层方法，获取布尔值
        is_last_photo = photos_page.swipe_to_last_photo(max_swipes=8)

        # 断言布尔值（你的核心诉求）
        assert is_last_photo is True, f"未滑到最后一张图片，返回值：{is_last_photo}"
        logger.info("===== Photos滑动用例成功 =====")

    except Exception as e:
        logger.error(f"用例失败：{e}")
        raise e
