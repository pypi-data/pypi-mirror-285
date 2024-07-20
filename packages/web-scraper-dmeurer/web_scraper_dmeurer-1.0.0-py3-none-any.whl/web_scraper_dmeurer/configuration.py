# Parser for command line arguments
import argparse
# parse the dict arguments
import json


class Settings:
    """
    Settings

    This class is used to store the settings for the AI.
    The settings are used to configure the AI to work with different websites.
    """

    def __init__(
            self,
            base_url: str = "",
            base_url_paging_prefix: str = "",
            base_url_paging_suffix: str = "",
            pages_required: bool = False,
            page_start: int = 0,
            page_step: int = 0,
            page_end: int = 0,
            recursive_navigation: dict = None,
            product_element_css_selector: str = "",
            product_site_needed: bool = False,
            product_site_link_css_selector: str = "",
            product_site_link_prefix: str = "",
            product_data_extraction: dict = None,
            verbose_output: bool = False,
            custom_http_headers: dict = None,
            url_blacklist_regex: str = "",
            output_file_path: str = "./scraped_data.csv",
            warning_tag_if_present: str = "",
            request_delay: int = 0
    ):
        """
        __init__(base_url: str = "", base_url_paging_prefix: str = "", base_url_paging_suffix: str = "", pages_required: bool = False, page_start: int = 0, page_step: int = 0, page_end: int = 0, recursive_navigation: dict = None, product_element_css_selector: str = "", product_site_needed: bool = False, product_site_link_css_selector: str = "", product_site_link_prefix: str = "", product_data_extraction: dict = None, verbose_output: bool = False, custom_http_headers: dict = None, url_blacklist_regex: str = "")

        :param str base_url: The base url of the website.
        :param str base_url_paging_prefix: The beginning of the base url.
        :param str base_url_paging_suffix: The end of the base url.
        :param bool pages_required: If the pages are required.
        :param int page_start: The page number to start with
        :param int page_step: The step between the pages.
        :param int page_end: The end of the page stepper. This number is excluded. So wit will download until x < num, not x <= num.
        :param list recursive_navigation: List of css selectors to navigate through the website. Used to enable users to only paste the link for the first page, and the AI will navigate through the website. A JSON object with 'css_selector' and optional 'base_url_in_case_links_are_relative' can be provided.
        :param bool product_site_needed: Whether the product site is needed and should be downloaded.
        :param str product_site_link_css_selector: The product site link css selector
        :param bool verbose_output: If the output should be verbose
        :param dict custom_http_headers: Custom HTTP headers to use for the requests. Default is a user agent for an iPad.
        :param str url_blacklist_regex: A regex to match URLs that should be ignored. Default is an empty string.
        :param str output_file_path: The path to the output CSV file. Default is "./scraped_data.csv"
        :param str warning_tag_if_present: Creates a column "Warning" if the css selector finds an element.
        """

        # defaults for JSON objects
        if product_data_extraction is None:
            self.__product_data_extraction = [{"column_name": "Name", "css_selector": ".product-name"}, {"column_name": "ID", "css_selector": ".product-id"}]
        else:
            self.__product_data_extraction = product_data_extraction
        if recursive_navigation is None:
            self.__recursive_navigation = [{"css_selector": ".category"}]
        else:
            self.__recursive_navigation = recursive_navigation
        if custom_http_headers is None:
            self.__custom_http_headers = {
                'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
            }
        else:
            self.__custom_http_headers = custom_http_headers

        # apply settings
        self.__base_url = base_url
        self.__base_url_paging_prefix = base_url_paging_prefix
        self.__base_url_paging_suffix = base_url_paging_suffix
        self.__pages_required = pages_required
        self.__page_start = page_start
        self.__page_step = page_step
        self.__page_end = page_end
        self.__recursive_navigation = recursive_navigation
        self.__product_element_css_selector = product_element_css_selector
        self.__product_site_needed = product_site_needed
        self.__product_site_link_css_selector = product_site_link_css_selector
        self.__product_site_link_prefix = product_site_link_prefix
        self.__verbose_output = verbose_output
        self.__url_blacklist_regex = url_blacklist_regex
        self.__output_file_path = output_file_path
        self.__warning_tag_if_present = warning_tag_if_present
        self.__request_delay = request_delay

        self.disable_integrity_check = False

        self.check_integrity()

    def check_integrity(self):
        if self.disable_integrity_check:
            print("[SETTINGS] Integrity check called, but was disabled.")
            return
        # check if there are errors in the configuration of the product site
        self.check_product_site()
        # check pages
        self.check_pageing()
        # check if some features are activated that are not implemented yet
        self.check_not_implemented()
        # check if request delay is ok
        self.check_request_delay()

    def check_product_site(self):
        """
        Check if the product site is needed and if the css selector is set.
        :return:
        """
        if self.__product_site_needed and self.__product_site_link_css_selector == "":
            raise Exception("[SETTINGS] The product site is needed but no css selector is specified.")

        if not self.__product_site_needed and self.__product_site_link_css_selector != "":
            print("[SETTINGS] WARNING The product site is not needed but a css selector is specified. The css selector will be ignored.")

    def check_pageing(self):
        """
        Check if the pageing is set correctly.
        :return:
        """
        if not self.__pages_required:
            return

        if self.__page_start > self.__page_end:
            print("[SETTINGS] WARNING page_start is greater than __page_end. Swapping values.")
            self.__page_end, self.__page_start = self.__page_start, self.__page_end

        if self.__page_start == self.__page_end:
            raise Exception("[SETTINGS] page_start is equal to page_end. This will result in no page being loaded.\nPlease note that __page_end is excluded from the loading. So if you want to load until page 5, you have to set __page_end to 6.\n(Currently: page_start: " + str(self.__page_start) + ", page_end: " + str(self.__page_end) + ")")

        if self.__page_step < 1:
            raise Exception("[SETTINGS] page_step is less than 1. This will result in an infinite loop. Please set page_step to a number greater than 0.")

        if self.__page_start == self.__page_end - 1:
            print("[SETTINGS] WARNING The page_end is only one page greater than page_start. This will result in only one page being loaded.\nYou might want to set __page_end to a higher number or disable the paging option.")

    def check_not_implemented(self):
        """
        Check if some features are activated that are not implemented yet.
        :return:
        """
        pass

    def check_request_delay(self):
        """
        Check if the request delay is set correctly.
        :return:
        """
        if self.__request_delay < 0:
            raise Exception("[SETTINGS] The request delay is less than 0. This will result in an infinite loop. Please set the request delay to a number greater than 0.")
        if self.__request_delay < 100:
            print("[SETTINGS] WARNING The request delay is less than 100 milliseconds. This might result in a high load on the server. In some cases this might result in the server blocking your IP. Please set the request delay to a number greater than 100 milliseconds.")
        if self.__request_delay > 10000:
            print("[SETTINGS] WARNING The request delay is greater than 10 seconds. This might result in a slow scraping process. Please set the request delay to a number less than 10000 milliseconds.")

    def get_base_url(self) -> str:
        """
        Get the base url of the website.
        :return: str
        """
        return self.__base_url

    def get_base_url_paging_prefix(self) -> str:
        """
        Get the beginning of the base url.
        :return: str
        """
        return self.__base_url_paging_prefix

    def get_base_url_paging_suffix(self) -> str:
        """
        Get the end of the base url.
        This is the part added to the url after the page number.
        :return: str
        """
        return self.__base_url_paging_suffix

    def get_pages_required(self) -> bool:
        """
        Get if the pages are required.
        :return: bool
        """
        return self.__pages_required

    def get_page_start(self) -> int:
        """
        Get the page number of the first page.
        :return: int
        """
        return self.__page_start

    def get_page_step(self) -> int:
        """
        Get the step size between the pages.
        :return: int
        """
        return self.__page_step

    def get_page_end(self) -> int:
        """
        Get the page number of the last page.
        Warning: This number is excluded from the loading.
        So if you want to load until page 5, you have to set page_end to 6.
        :return:
        """
        return self.__page_end

    def get_recursive_navigation(self) -> dict:
        """
        Get the recursive navigation list.
        This is a list of css selectors to navigate through the website. Used to enable users to only paste the link for the first page and the AI will navigate through the website.
        :return: dict
        """
        return self.__recursive_navigation

    def get_product_element_css_selector(self) -> str:
        """
        Get the product element css selector.
        :return: str
        """
        return self.__product_element_css_selector

    def get_product_site_needed(self) -> bool:
        """
        Get if the product site is needed and should be downloaded.
        :return:
        """
        return self.__product_site_needed

    def get_product_site_link_css_selector(self) -> str:
        """
        Get the product site link css selector.
        :return: str
        """
        return self.__product_site_link_css_selector

    def get_product_site_link_prefix(self) -> str:
        """
        Get the product site link prefix.
        :return: str
        """
        return self.__product_site_link_prefix

    def get_product_data_extraction(self) -> dict:
        """
        Get a JSON object with css selectors of the product data.
        :return: list
        """
        return self.__product_data_extraction

    def get_verbose_output(self) -> bool:
        """
        Get if the output should be verbose.
        :return: bool
        """
        return self.__verbose_output

    def get_custom_http_headers(self) -> dict:
        """
        Get the custom HTTP headers.
        :return: dict
        """
        return self.__custom_http_headers

    def get_url_blacklist_regex(self) -> str:
        """
        Get the regex to match URLs that should be ignored.
        :return: str
        """
        return self.__url_blacklist_regex

    def get_output_file_path(self) -> str:
        """
        Get the output file.
        :return: str
        """
        return self.__output_file_path

    def get_warning_tag_if_present(self) -> str:
        """
        Get the warning tag if present.
        :return: str
        """
        return self.__warning_tag_if_present

    def get_request_delay(self) -> int:
        """
        Get the request delay.
        :return: int
        """
        return self.__request_delay

    def set_base_url(self, base_url: str):
        """
        Set the base url of the website.
        :param str base_url:
        :return: self
        """
        self.__base_url = base_url
        return self

    def set_base_url_paging_prefix(self, base_url_prefix: str):
        """
        Set the beginning of the base url.
        :param str base_url_prefix:
        :return: self
        """
        self.__base_url_paging_prefix = base_url_prefix
        return self

    def set_base_url_paging_suffix(self, base_url_paging_suffix: str):
        """
        Set the end of the base url.
        This is the part added to the url after the page number.
        :param str base_url_paging_suffix:
        :return: self
        """
        self.__base_url_paging_suffix = base_url_paging_suffix
        return self

    def set_pages_required(self, pages_required: bool):
        """
        Set if the pages are required.
        :param bool pages_required:
        :return: self
        """
        self.__pages_required = pages_required
        return self

    def set_page_start(self, page_start: int):
        """
        Set the page number of the first page.
        :param int page_start:
        :return: self
        """
        self.__page_start = page_start
        self.check_integrity()
        return self

    def set_page_step(self, page_step: int):
        """
        Set the step size between the pages.
        :param int page_step:
        :return: self
        """
        self.__page_step = page_step
        self.check_integrity()
        return self

    def set_page_end(self, page_end: int):
        """
        Set the page number of the last page.
        Warning: This number is excluded from the loading.
        So if you want to load until page 5, you have to set page_end to 6.
        :param int page_end:
        :return: self
        """
        self.__page_end = page_end
        self.check_integrity()
        return self

    def set_page_range(self, page_start: int, page_end: int, page_step: int):
        """
        Set the page range.
        :param int page_start: The page number of the first page.
        :param int page_end: The page number of the last page. Warning: This number is excluded from the loading. So if you want to load until page 5, you have to set page_end to 6.
        :param int page_step: The step size between the pages.
        :return: self
        """
        self.__page_start = page_start
        self.__page_end = page_end
        self.__page_step = page_step
        self.check_integrity()
        return self

    def set_recursive_navigation(self, navigate_categories: dict):
        """
        Set the recursive navigation list. Leave empty to disable recursive navigation.
        This is a list of css selectors to navigate through the website. Used to enable users to only paste the link for the first page and the AI will navigate through the website.
        Every JSON object should have a 'css_selector' and an optional 'base_url_in_case_links_are_relative'.
        :param list navigate_categories: JSON object with 'css_selector' and optional 'base_url_in_case_links_are_relative'
        :return: self
        """
        self.__recursive_navigation = navigate_categories
        return self

    def set_product_element_css_selector(self, product_element_css_selector: str):
        """
        Set the product element css selector.
        :param str product_element_css_selector:
        :return: self
        """
        self.__product_element_css_selector = product_element_css_selector
        return self

    def set_product_site_needed(self, product_site_needed: bool):
        """
        Set if the product site is needed and should be downloaded.
        :param bool product_site_needed:
        :return: self
        """
        self.__product_site_needed = product_site_needed
        return self

    def set_product_site_link_css_selector(self, product_site_link_css_selector: str):
        """
        Set the product site link css selector.
        :param str product_site_link_css_selector:
        :return: self
        """
        self.__product_site_link_css_selector = product_site_link_css_selector
        return self

    def set_product_site_link_prefix(self, product_site_link_prefix: str):
        """
        Set the product site link prefix.
        :param str product_site_link_prefix:
        :return: self
        """
        self.__product_site_link_prefix = product_site_link_prefix
        return self

    def set_product_data_extraction(self, product_data_extraction: list):
        """
        Set the product data extraction list.
        :param list product_data_extraction: JSON array where each object has 'column_name' and 'css_selector'.
        :return: self
        """
        self.__product_data_extraction = product_data_extraction
        return self

    def set_verbose_output(self, verbose_output: bool):
        """
        Set if the output should be verbose.
        :param bool verbose_output: True if the output should be verbose.
        :return: self
        """
        self.__verbose_output = verbose_output
        return self

    def set_custom_http_headers(self, custom_http_headers: dict):
        """
        Set the custom HTTP headers.
        :param dict custom_http_headers: JSON object with the custom HTTP headers.
        :return: self
        """
        self.__custom_http_headers = custom_http_headers
        return self

    def set_url_blacklist_regex(self, url_blacklist_regex: str):
        """
        Set the regex to match URLs that should be ignored.
        The default is an empty string.
        The IGNORE-CASE flag is enabled, so the regex is case-insensitive.
        An example regex to match social media URLs is: ".*((instagram)|(facebook)|(twitter)|(linkedin)|(youtube)|(login)|(spotify)|(contact)).*"
        Personally, I would recommend using something like https://regexr.com/7u5v4 to test your regex.
        :param str url_blacklist_regex: The regex string.
        :return: self
        """
        self.__url_blacklist_regex = url_blacklist_regex
        return self

    def set_output_file_path(self, output_file_path: str):
        """
        Set the output file.
        :param str output_file_path: The path to the output CSV file. Default is "./scraped_data.csv"
        :return: self
        """
        self.__output_file_path = output_file_path
        return self

    def set_warning_tag_if_present(self, warning_tag_if_present: str):
        """
        This will create a column "Warning" if the css selector finds an element.
        :param str warning_tag_if_present: CSS selector to check for.
        :return: self
        """
        self.__warning_tag_if_present = warning_tag_if_present
        return self

    def set_request_delay(self, request_delay: int):
        """
        Set the request delay.
        :param int request_delay: The request delay in milliseconds.
        :return: self
        """
        self.__request_delay = request_delay
        self.check_request_delay()
        return self

    def set_settings(self, settings_dict: dict):
        """
        Set the settings from a dictionary.

        :param settings_dict:
        :return:
        """

        self.disable_integrity_check = True

        if "settings.get_base_url" in settings_dict:
            self.set_base_url(settings_dict["settings.get_base_url"])
        if "base_url_paging_prefix" in settings_dict:
            self.set_base_url_paging_prefix(settings_dict["base_url_paging_prefix"])
        if "base_url_paging_suffix" in settings_dict:
            self.set_base_url_paging_suffix(settings_dict["base_url_paging_suffix"])
        if "pages_required" in settings_dict:
            self.set_pages_required(settings_dict["pages_required"])
        if "page_start" in settings_dict:
            self.set_page_start(settings_dict["page_start"])
        if "page_step" in settings_dict:
            self.set_page_step(settings_dict["page_step"])
        if "page_end" in settings_dict:
            self.set_page_end(settings_dict["page_end"])
        if "recursive_navigation" in settings_dict:
            self.set_recursive_navigation(settings_dict["recursive_navigation"])
        if "product_element_css_selector" in settings_dict:
            self.set_product_element_css_selector(settings_dict["product_element_css_selector"])
        if "product_site_needed" in settings_dict:
            self.set_product_site_needed(settings_dict["product_site_needed"])
        if "product_site_link_css_selector" in settings_dict:
            self.set_product_site_link_css_selector(settings_dict["product_site_link_css_selector"])
        if "verbose_output" in settings_dict:
            self.set_verbose_output(settings_dict["verbose_output"])
        if "custom_http_headers" in settings_dict:
            self.set_custom_http_headers(settings_dict["custom_http_headers"])
        if "url_blacklist_regex" in settings_dict:
            self.set_url_blacklist_regex(settings_dict["url_blacklist_regex"])
        if "product_data_extraction" in settings_dict:
            self.set_product_data_extraction(settings_dict["product_data_extraction"])
        if "product_site_link_prefix" in settings_dict:
            self.set_product_site_link_prefix(settings_dict["product_site_link_prefix"])
        if "output_file_path" in settings_dict:
            self.set_output_file_path(settings_dict["output_file_path"])
        if "warning_tag_if_present" in settings_dict:
            self.set_warning_tag_if_present(settings_dict["warning_tag_if_present"])
        if "request_delay" in settings_dict:
            self.set_request_delay(settings_dict["request_delay"])

        self.disable_integrity_check = False
        self.check_integrity()
        return self

    def get_settings(self) -> dict:
        """
        Get the settings as a dictionary.
        This is useful for saving the settings to a file.
        :return:  dict
        """
        return {
            "settings.get_base_url": self.__base_url,
            "base_url_paging_prefix": self.__base_url_paging_prefix,
            "base_url_paging_suffix": self.__base_url_paging_suffix,
            "pages_required": self.__pages_required,
            "page_start": self.__page_start,
            "page_step": self.__page_step,
            "page_end": self.__page_end,
            "recursive_navigation": self.__recursive_navigation,
            "product_element_css_selector": self.__product_element_css_selector,
            "product_site_needed": self.__product_site_needed,
            "product_site_link_css_selector": self.__product_site_link_css_selector,
            "product_site_link_prefix": self.__product_site_link_prefix,
            "product_data_extraction": self.__product_data_extraction,
            "verbose_output": self.__verbose_output,
            "custom_http_headers": self.__custom_http_headers,
            "url_blacklist_regex": self.__url_blacklist_regex,
            "output_file_path": self.__output_file_path,
            "warning_tag_if_present": self.__warning_tag_if_present,
            "request_delay": self.__request_delay
        }

    def get_settings_json(self) -> str:
        """
        Get the settings as a JSON string.
        This is useful for saving the settings to a file.
        :return:  str
        """
        return json.dumps(self.get_settings())

    def parse_args(self, args):

        self.disable_integrity_check = True

        parser = argparse.ArgumentParser(description='Settings for the Web Scraper')

        parser.add_argument('--config_file', type=str, help='The path to the config file. This will load before the other settings, so the settings in the file can be overwritten by the command line arguments.')

        parser.add_argument('--base_url', type=str, help='The base url of the website.')
        parser.add_argument('--base_url_paging_prefix', type=str, help='The beginning of the base url.')
        parser.add_argument('--base_url_paging_suffix', type=str, help='The end of the base url.')
        parser.add_argument('--pages_required', type=bool, help='If the pages are required.')
        parser.add_argument('--page_start', type=int, help='The page number to start with')
        parser.add_argument('--page_step', type=int, help='The step between the pages.')
        parser.add_argument('--page_end', type=int, help='The end of the page stepper. This number is excluded. So wit will download until x < num, not x <= num.')
        parser.add_argument('--recursive_navigation', type=str, help='List of css selectors to navigate through the website. Used to enable users to only paste the link for the first page, and the AI will navigate through the website. A JSON object with "css_selector" and optional "base_url_in_case_links_are_relative" can be provided.')
        parser.add_argument('--product_element_css_selector', type=str, help='The product element css selector')
        parser.add_argument('--product_site_needed', type=bool, help='Whether the product site is needed and should be downloaded.')
        parser.add_argument('--product_site_link_css_selector', type=str, help='The product site link css selector')
        parser.add_argument('--product_site_link_prefix', type=str, help='The product site link prefix')
        parser.add_argument('--product_data_extraction', type=str, help='A JSON object with css selectors of the product data.')
        parser.add_argument('--verbose_output', type=bool, help='If the output should be verbose')
        parser.add_argument('--custom_http_headers', type=str, help='Custom HTTP headers to use for the requests. Default is a user agent for an iPad.')
        parser.add_argument('--url_blacklist_regex', type=str, help='A regex to match URLs that should be ignored. Default is an empty string.')
        parser.add_argument('--output_file_path', type=str, help='The path to the output CSV file. Default is "./scraped_data.csv"')
        parser.add_argument('--warning_tag_if_present', type=str, help='Creates a column "Warning" if the css selector finds an element.')
        parser.add_argument('--request_delay', type=int, help='The request delay in milliseconds.')

        args = parser.parse_args(args)

        if args.config_file:
            with open(args.config_file, 'r') as file:
                settings = json.load(file)
                self.set_settings(settings)

        if args.base_url:
            self.set_base_url(args.base_url)
        if args.base_url_paging_prefix:
            self.set_base_url_paging_prefix(args.base_url_paging_prefix)
        if args.base_url_paging_suffix:
            self.set_base_url_paging_suffix(args.base_url_paging_suffix)
        if args.pages_required:
            self.set_pages_required(args.pages_required)
        if args.page_start:
            self.set_page_start(args.page_start)
        if args.page_step:
            self.set_page_step(args.page_step)
        if args.page_end:
            self.set_page_end(args.page_end)
        if args.recursive_navigation:
            self.set_recursive_navigation(json.load(args.recursive_navigation))
        if args.product_element_css_selector:
            self.set_product_element_css_selector(args.product_element_css_selector)
        if args.product_site_needed:
            self.set_product_site_needed(args.product_site_needed)
        if args.product_site_link_css_selector:
            self.set_product_site_link_css_selector(args.product_site_link_css_selector)
        if args.product_site_link_prefix:
            self.set_product_site_link_prefix(args.product_site_link_prefix)
        if args.product_data_extraction:
            self.set_product_data_extraction(json.load(args.product_data_extraction))
        if args.verbose_output:
            self.set_verbose_output(args.verbose_output)
        if args.custom_http_headers:
            self.set_custom_http_headers(json.load(args.custom_http_headers))
        if args.url_blacklist_regex:
            self.set_url_blacklist_regex(args.url_blacklist_regex)
        if args.output_file_path:
            self.set_output_file_path(args.output_file_path)
        if args.warning_tag_if_present:
            self.set_warning_tag_if_present(args.warning_tag_if_present)
        if args.request_delay:
            self.set_request_delay(args.request_delay)

        self.disable_integrity_check = False
        self.check_integrity()

        return self

    def __str__(self):
        """
        __str__()
        :return: The settings as a JSON string
        """
        return str(self.get_settings())
