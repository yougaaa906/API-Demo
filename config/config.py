import os

TIMEOUT = 15
INPUT_TEXT = "Today is a sunny day!"
APPIUM_REMOTE_URL = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")

DESIRED_CAPS =  {
  "platformName": "Android",
  "deviceName": os.getenv("DEVICE_NAME", "Android Emulator"),
  "appPackage": "io.appium.android.apis",
  "appActivity": "io.appium.android.apis.ApiDemos",
  "automationName": "UiAutomator2",
  "noReset": False,
  "udid": os.getenv("DEVICE_UDID", ""),
  "newCommandTimeout": 30,
  "platformVersion": os.getenv("PLATFORM_VERSION", ""),
  "app": os.getenv("APP_PATH", "./apps/ApiDemos-debug.apk")
}

IMPLICIT_TIMEOUT = 10
HOME_ELEMENT = ("xpath", "//android.widget.TextView[@text='Accessibility']")
MAX_RETURN_TIMES = 5

