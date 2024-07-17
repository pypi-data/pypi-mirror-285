import os
import allure
import pytest
from datetime import datetime
from screeninfo.screeninfo import get_monitors
from playwright.sync_api._generated import Page
from framework.utils.utils import TestResultManager
from framework.config.mobile_config import MobileConfig
from framework.utils.create_general_directory import RESULTS_DIR


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config.option.allure_report_dir = os.path.join(RESULTS_DIR, 'Allure_Results')
    config.option.htmlpath = os.path.join(RESULTS_DIR, 'HTML_Results', 'BasicReport.html')
    config.option.output = os.path.join(RESULTS_DIR, 'Test_Results')


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    primary_monitor = get_monitors()[0]
    width = primary_monitor.width - 30
    height = primary_monitor.height - 140
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "permissions": ['geolocation'],
        "geolocation": {'longitude': 1, 'latitude': 1},
        "viewport": {"width": width, "height": height},
    }


@pytest.fixture(scope="function")
def page(page: Page):
    return page


@pytest.fixture(scope="function", autouse=True)
def before_test(page):
    TestResultManager.attach_artifact_folder_link_to_allure()
    # base_page = BasePage(page)
    # env_file_path = BasePage.get_file_location('env_config.json', file_extension=".json")
    # ENVIRONMENT = get_environment_config(env_file_path)
    # base_page.set_global_variable(environment_url=ENVIRONMENT.get('URL'))
    yield


@pytest.fixture(scope="function", autouse=True)
def after_test(page):
    yield
    print("after test yield")
    # base_page = BasePage(page)
    # base_page.attach_video_to_allure()


@pytest.fixture(scope="session", autouse=True)
def after_all():
    yield
    print("After All")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get('page')
        timestamp = datetime.now().strftime('%d-%m-%Y---%I-%M-%S-%p')
        screenshot_path = os.path.join(TestResultManager.get_test_output_dir(), "failure-screenshots",
                                       f"failure-screenshot_{timestamp}.png")
        page.screenshot(path=screenshot_path)
        allure.attach.file(screenshot_path, name=f"failure-screenshot_{timestamp}",
                           attachment_type=allure.attachment_type.PNG)


@pytest.fixture(scope='session')
def mobile_driver():
    config = MobileConfig(platform_name='Android', device_name='emulator-5554', app_path='/path/to/your/app.apk')
    driver = config.initialize_driver()
    yield driver
    driver.quit()
