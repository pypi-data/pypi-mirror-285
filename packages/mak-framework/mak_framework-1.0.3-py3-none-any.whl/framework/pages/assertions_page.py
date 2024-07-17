def print_colored(text, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m'
    }
    end_color = '\033[0m'
    if color in colors:
        return f"{colors[color]}{text}{end_color}"
    else:
        return text


class Assertions:
    def __init__(self, page):
        self.page = page

    def assert_element_has_text(self, selector, expected_text, timeout=1000, error_message=None):
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            actual_text = element.inner_text()
            assert expected_text in actual_text, (
                f"Element with selector '{selector}' does not contain the expected text. "
                f"Expected: '{expected_text}', Actual: '{actual_text}'"
            )
            print(
                print_colored(f"Assertion passed: Element contains expected text '{expected_text}'", 'green')
            )
        except TimeoutError:
            raise TimeoutError(f"Timeout waiting for element with selector '{selector}' to appear")
        except AssertionError as assertion_error:
            if error_message:
                raise AssertionError(error_message)
            else:
                raise AssertionError(assertion_error)
        except Exception as e:
            raise AssertionError(f"An error occurred: {str(e)}")

    def assert_element_attribute_value(self, selector, attribute, expected_value, timeout=1000, error_message=None):
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            actual_value = element.get_attribute(attribute)
            assert actual_value == expected_value, (
                f"Element with selector '{selector}' has attribute '{attribute}' "
                f"value '{actual_value}' instead of expected '{expected_value}'"
            )
            print(print_colored(
                f"Assertion passed: Element attribute '{attribute}' VALUE '{actual_value}' matches expected '{expected_value}'",'green'))
        except TimeoutError:
            raise TimeoutError(f"Timeout waiting for element with selector '{selector}' to appear")
        except AssertionError as assertion_error:
            if error_message:
                raise AssertionError(error_message)
            else:
                raise AssertionError(assertion_error)

    def assert_page_title(self, expected_title):
        actual_title = self.page.title()
        assert actual_title == expected_title, f"Page title is '{actual_title}' instead of expected title '{expected_title}'"

    def assert_element_exists(self, selector):
        assert self.page.locator(selector).exists(), f"Element with selector '{selector}' does not exist"

    def assert_element_not_exists(self, selector):
        assert not self.page.locator(selector).exists(), f"Element with selector '{selector}' should not exist"

    def assert_element_visible(self, selector, timeout: int = None):
        self.page.wait_for_selector(selector, timeout=timeout)
        assert self.page.locator(selector).is_visible(), f"Element with selector '{selector}' is not visible"

    def assert_element_not_visible(self, selector):
        assert not self.page.locator(selector).is_visible(), f"Element with selector '{selector}' should not be visible"

    def assert_element_has_class(self, selector, class_name):
        assert class_name in self.page.locator(selector).get_attribute(
            'class'), f"Element with selector '{selector}' does not have the class '{class_name}'"

    def assert_page_contains_text(self, expected_text):
        page_content = self.page.inner_text()
        assert expected_text in page_content, (f"Page content does not contain the expected text. "
                                               f"Expected: {expected_text}, "f"Actual: {page_content}")

    def assert_page_does_not_contain_text(self, unexpected_text):
        page_content = self.page.inner_text()
        assert unexpected_text not in page_content, (f"Page content should not contain the text: "
                                                     f"{unexpected_text}, but it does")

    def assert_element_enabled(self, selector):
        assert self.page.locator(selector).is_enabled(), f"Element with selector '{selector}' is not enabled"

    def assert_element_disabled(self, selector):
        assert not self.page.locator(selector).is_enabled(), f"Element with selector '{selector}' should be disabled"

    def assert_element_attribute_contains(self, selector, attribute, expected_value):
        actual_value = self.page.locator(selector).get_attribute(attribute)
        assert expected_value in actual_value, (f"Element with selector '{selector}' attribute '{attribute}' "
                                                f"does not contain the expected value '{expected_value}'")

    def assert_element_attribute_not_contains(self, selector, attribute, unexpected_value):
        actual_value = self.page.locator(selector).get_attribute(attribute)
        assert unexpected_value not in actual_value, (f"Element with selector '{selector}' attribute '{attribute}' "
                                                      f"should not contain the value '{unexpected_value}'")

    def assert_element_checked(self, selector):
        assert self.page.locator(selector).is_checked(), f"Element with selector '{selector}' is not checked"

    def assert_element_not_checked(self, selector):
        assert not self.page.locator(selector).is_checked(), f"Element with selector '{selector}' should not be checked"

    def assert_element_displayed(self, selector):
        """Asserts that the element identified by the selector is displayed."""
        assert self.page.locator(selector).is_displayed(), f"Element with selector '{selector}' is not displayed"

    def assert_element_not_displayed(self, selector):
        """Asserts that the element identified by the selector is not displayed."""
        assert not self.page.locator(
            selector).is_displayed(), f"Element with selector '{selector}' should not be displayed"

    def assert_element_has_attribute(self, selector, attribute):
        assert self.page.locator(selector).has_attribute(
            attribute), f"Element with selector '{selector}' does not have attribute '{attribute}'"

    def assert_element_has_no_attribute(self, selector, attribute):
        assert not self.page.locator(selector).has_attribute(
            attribute), f"Element with selector '{selector}' should not have attribute '{attribute}'"

    def assert_element_attribute_not_empty(self, selector, attribute):
        actual_value = self.page.locator(selector).get_attribute(attribute)
        assert actual_value, f"Element with selector '{selector}' attribute '{attribute}' is empty"

    def assert_element_attribute_empty(self, selector, attribute):
        actual_value = self.page.locator(selector).get_attribute(attribute)
        assert not actual_value, f"Element with selector '{selector}' attribute '{attribute}' is not empty"

    def assert_element_text_contains(self, selector, expected_substring):
        actual_text = self.page.locator(selector).inner_text()
        assert expected_substring in actual_text, (
            f"Element with selector '{selector}' does not contain the expected substring. "
            f"Expected: {expected_substring}, Actual: {actual_text}")

    def assert_element_text_not_contains(self, selector, unexpected_substring):
        actual_text = self.page.locator(selector).inner_text()
        assert unexpected_substring not in actual_text, (
            f"Element with selector '{selector}' should not contain the substring: "
            f"{unexpected_substring}, but it does")

