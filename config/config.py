TIMEOUT = 15
INPUT_TEXT = "Today is a sunny day!"
APPIUM_REMOTE_URL = "http://127.0.0.1:4723"

DESIRED_CAPS =  {
  "platformName": "Android",
  "deviceName": "LDPlayer",
  "appPackage": "io.appium.android.apis",
  "appActivity": "io.appium.android.apis.ApiDemos",
  "automationName": "UiAutomator2",
  "noReset": False,
  "udid": "emulator-5554",
  "newCommandTimeout": 30
}
IMPLICIT_TIMEOUT = 10
HOME_ELEMENT = ("xpath", "//android.widget.TextView[@text='Accessibility']")
MAX_RETURN_TIMES = 5