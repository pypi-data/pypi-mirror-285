import time
from framework.utils.utils import LoggerUtils
from playwright.sync_api._generated import Page
from framework.core.actions_enums import actions
from framework.pages.assertions_page import Assertions
from framework.utils.exception_handling import handle_exceptions


logger = LoggerUtils()


class BasePage:
    global_variables = {}
    # Timeout = 50


    def __init__(self, page: Page):
        self.page = page
        self.assertions = Assertions(self.page)

    def set_global_variable(self, **values):
        try:
            self.global_variables.update(values)
        except Exception as exp:
            selectors_list = []
            self.print_error_message(selectors_list, exp,
                                     custom_message=f"Error setting up global variable in dictionary: {exp}")

    def use_global_variable(self, key):
        if key in self.global_variables:
            return self.global_variables[key]
        else:
            selectors_list = []
            self.print_error_message(selectors_list, key,
                                     custom_message=f"Key {key} not found in global variables in dictionary")

    def show_all_global_variables(self):
        self.print_message("Global Variables: ")
        for key, value in self.global_variables.items():
            self.print_message(key, value, color='green')

    def show_dictionary(self):
        print("\n")
        keys = self.global_variables.keys()
        self.print_message(keys, color="red")

        values = self.global_variables.values()
        self.print_message(values, color="red")

        items = self.global_variables.items()
        self.print_message(items, color="red")

    def clear_all_values(self):
        self.global_variables.clear()

    def print_message(self, *texts, color: str = "green") -> None:
        """Prints messages with optional color formatting."""
        self.page.wait_for_timeout(1)
        color_codes = {
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "magenta": "35",
            "cyan": "36",
            "white": "37"
        }

        if color not in color_codes:
            raise ValueError(f"Invalid color '{color}'. Supported colors: {', '.join(color_codes.keys())}")

        formatted_texts = [f"\033[1;{color_codes[color]}m{text}\033[0m" for text in texts]
        formatted_message = ' '.join(formatted_texts)
        print(formatted_message)

    def print_error_message(self, selectors: list, e: Exception, custom_message: str = None, optional: bool = False) -> None:
        """Prints error messages with optional custom message."""
        self.page.wait_for_timeout(1)

        if custom_message:
            error_message = custom_message
        else:
            selector_string = ', '.join(map(str, selectors))
            error_message = f"Error Message {selector_string}: {e}"

        formatted_error = f"\033[1;31m{error_message}\033[0m"

        if optional:
            print(formatted_error)
        else:
            if logger:
                logger.log_error(formatted_error)
            else:
                print(formatted_error)

    def is_element_visible(self, selector, timeout):
        try:
            element = self.page.wait_for_selector(selector, state='visible', timeout=timeout)
            return True
        except:
            return False

    @staticmethod
    def _perform_assertions(element, assertions, selector):
        if assertions:
            for assertion_type in assertions:
                if assertion_type == "visible":
                    passed = element.is_visible()
                    if not passed:
                        return False, f"Element with selector '{selector}' is not visible"
                elif assertion_type == "enabled":
                    passed = element.is_enabled()
                    if not passed:
                        return False, f"Element with selector '{selector}' is not enabled"
                elif assertion_type == "hidden":
                    passed = element.is_hidden()
                    if not passed:
                        return False, f"Element with selector '{selector}' is not hidden"
                elif assertion_type == "editable":
                    passed = element.is_editable()
                    if not passed:
                        return False, f"Element with selector '{selector}' is not editable"
                elif assertion_type == "checked":
                    passed = element.is_checked()
                    if not passed:
                        return False, f"Element with selector '{selector}' is not checked"
                elif assertion_type == "disabled":
                    passed = element.is_disabled()
                    if not passed:
                        return False, f"Element with selector '{selector}' is not disabled"
        return True, "Assertions passed"

    def _assert_expected_text(self, element, selector, expected_text):
        """
        Asserts whether the text of the given element matches the expected text.

        Parameters:
            element: Element to check the text content.
            selector (str): Selector of the element.
            expected_text (str): Expected text content.

        Raises:
            AssertionError: If the actual text does not contain the expected text.
        """
        actual_text = str(element.text_content()).lower()
        expected_text = str(expected_text).lower()
        assert expected_text in actual_text, (
            f"Text of element with selector '{selector}' does not contain the expected text. "
            f"Actual: '{actual_text}', Expected: '{expected_text}'")
        self.print_message(f"Message : {actual_text}", color="yellow")

    def _assert_attribute_value(self, element, attribute, value):
        """
        Asserts whether the attribute of the given element matches the expected value.

        Parameters:
            element: Element to check the attribute value.
            attribute (str): Name of the attribute.
            value: Expected value of the attribute.

        Raises:
            AssertionError: If the actual attribute value does not match the expected value.
        """
        attribute_actual_value = element.get_attribute(attribute)
        assert attribute_actual_value == value, (
            f"Attribute '{attribute}' is not as expected. "
            f"Actual: '{attribute_actual_value}', Expected: '{value}'")
        self.print_message(f"Message : {attribute_actual_value}", color="yellow")


    @handle_exceptions
    def perform_action(self, action, *args, assertions=None, expected_text=None,
                       assert_attribute=None, attribute_value=None, delay=None, **kwargs):
        """
        Perform various actions on a web page element.

        :param action: Action to be performed (e.g., "click", "fill", "select_option").
        :param args: Positional arguments for the action.
        :param assertions: List of assertion types to perform (e.g., ["visible", "enabled", "editable"]).
        :param expected_text: Expected text content of the element.
        :param assert_attribute: If provided, assert that the attribute has a specific value.
        :param attribute_value: Expected value of the attribute.
        :param delay: Optional delay before performing the action.
        :param kwargs: Additional keyword arguments for the action.

        :return: Result of the action.
        """
        default_delay = 0.2
        action_dict = {
            actions.CLICK: self.page.click,
            actions.FILL: self.page.fill,
            actions.SELECT_OPTION: self.page.select_option,
            actions.TYPE: self.page.type,
            actions.HOVER: self.page.hover,
            actions.PRESS: self.page.press,
            actions.WAIT_FOR_SELECTOR: self.page.wait_for_selector,
            actions.GET_ATTRIBUTE: self.page.get_attribute,
            actions.GET_TEXT: self.page.get_by_text,
            actions.EVAL_ON_SELECTOR: self.page.eval_on_selector,
            actions.FOCUS: self.page.focus,
            actions.DOUBLE_CLICK: self.page.dblclick,
            actions.TEXT_CONTENT: lambda *a, **k: self.page.locator(args[0]).text_content(),
            actions.LOCATOR: self.page.locator,
            actions.GET_BY_TEXT_CLICK: lambda *a, **k: self.page.get_by_text(args[0]).click(),
            actions.CHECK: self.page.check,
            actions.UNCHECK: self.page.uncheck,
            actions.WAIT_FOR_TIMEOUT: self.page.wait_for_timeout,
            actions.WAIT_FOR_LOAD_STATE: self.page.wait_for_load_state,
            actions.GO_BACK: self.page.go_back,
            actions.GO_FORWARD: self.page.go_forward,
            actions.RELOAD: self.page.reload,
            actions.CLOSE: self.page.close,
            actions.EVALUATE: self.page.evaluate,
            actions.EVALUATE_HANDLE: self.page.evaluate_handle,
            actions.EVAL_ON_SELECTOR_ALL: self.page.eval_on_selector_all,
            actions.SET_VIEWPORT_SIZE: self.page.set_viewport_size,
            actions.SET_CONTENT: self.page.set_content,
            actions.ADD_SCRIPT_TAG: self.page.add_script_tag,
            actions.ADD_STYLE_TAG: self.page.add_style_tag,
            actions.BRING_TO_FRONT: self.page.bring_to_front,
            actions.DISPATCH_EVENT: self.page.dispatch_event,
            actions.EXPOSE_FUNCTION: self.page.expose_function,
            actions.IS_CHECKED: self.page.is_checked,
            actions.IS_DISABLED: self.page.is_disabled,
            actions.IS_EDITABLE: self.page.is_editable,
            actions.IS_ENABLED: self.page.is_enabled,
            actions.IS_HIDDEN: self.page.is_hidden,
            actions.IS_VISIBLE: self.page.is_visible,
            actions.KEYBOARD: self.page.keyboard,
            actions.MOUSE: self.page.mouse,
            actions.INNER_TEXT: self.page.inner_text,
            actions.INNER_HTML: self.page.inner_html,
            actions.GOTO: self.page.goto,
            actions.GET_BY_ROLE: self.page.get_by_role,
            actions.QUERY_SELECTOR_ALL: self.page.query_selector_all,
            actions.PRESS_SEQUENTIALLY: lambda *a, **k: self.page.locator(args[0]).press_sequentially(args[1], delay=100),
        }

        element = self.page.locator(args[0])

        if delay is None:
            delay = default_delay

        time.sleep(delay)

        assertions_passed, message = self._perform_assertions(element, assertions, args[0])
        if not assertions_passed:
            self.print_message(message, color="red")
            return False

        if assert_attribute:
            self._assert_attribute_value(element, assert_attribute, attribute_value)

        if expected_text:
            self._assert_expected_text(element, args[0], expected_text)

        selected_action = action_dict.get(action)
        if selected_action:

            result = selected_action(*args, **kwargs)
            logger.log_info(f"Performed action: {action}, Args: {args}")
            return result
        else:
            raise ValueError("Invalid action specified")


