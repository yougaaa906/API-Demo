import os

# Global config
TIMEOUT = 30
INPUT_TEXT = "Today is a sunny day!"
MAX_RETURN_TIMES = 5

# BrowserStack config
BS_USERNAME = os.getenv("BS_USERNAME", "ruiruixiao_HBwtCk")
BS_ACCESS_KEY = os.getenv("BS_ACCESS_KEY", "6DpJ8BujqYbktEBhJSsp")
APPIUM_REMOTE_URL = f"https://{BS_USERNAME}:{BS_ACCESS_KEY}@hub.browserstack.com/wd/hub"

# Project path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = "API_Demo"
LOG_DIR = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}_logs")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}_screenshots")
REPORTS_DIR = os.path.join(PROJECT_ROOT, f"{PROJECT_NAME}_reports")

# Android desired capabilities
DESIRED_CAPS = {
    "platformName": "Android",
    "deviceName": os.getenv("DEVICE_NAME", "Google Pixel 3"),
    "automationName": "UiAutomator2",
    "noReset": False,
    "newCommandTimeout": 30,
    "platformVersion": os.getenv("PLATFORM_VERSION", "9.0"),
    "app": os.getenv("APP_PATH", "bs://19db12aefeee97f9eed40b499feb88911af3100e"),
    "bstack:options": {
        "userName": BS_USERNAME,
        "accessKey": BS_ACCESS_KEY,
        "projectName": "API_Demo",
        "buildName": "GitHub-Actions",
        "sessionName": "API_Demo-Test"
    }
}

# Element locator
HOME_ELEMENT = ("xpath", "//android.widget.TextView[@text='Accessibility']")
