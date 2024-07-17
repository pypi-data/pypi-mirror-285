from appium import webdriver


class MobileConfig:
    def __init__(self, platform_name, device_name, app_path, appium_server_url='http://localhost:4723/wd/hub'):
        self.platform_name = platform_name
        self.device_name = device_name
        self.app_path = app_path
        self.appium_server_url = appium_server_url

    def get_desired_capabilities(self):
        return {
            'platformName': self.platform_name,
            'deviceName': self.device_name,
            'app': self.app_path,
            'automationName': 'Appium'
        }

    def initialize_driver(self):
        return webdriver.Remote(self.appium_server_url, self.get_desired_capabilities())
