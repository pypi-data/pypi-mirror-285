# creating deep copys of objects
import copy
# for command line arguments
# http(s) requests
import requests
# parsing html
from bs4 import BeautifulSoup
# regex for the regex blacklist
import re
# storing data
import pandas as pd
# just to make something NaN
import numpy as np
# for request delay
import time
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


class Scraper:

    def __current_milli_time(self):
        return round(time.time() * 1000)

    def __init__(self, settings: Settings = Settings()):
        self.statistics = {
            "requests": 0,
            "failed_requests": 0,
            "duplicates": 0,
            "warnings": 0
        }
        self.settings = settings
        self.last_request_timestamp = self.__current_milli_time()

    def __append_base_url_if_relative(self, base_url: str, url: str) -> str:
        """
        Append the base url to the url if it is relative.
        Checks if the url starts with http, if not, it appends the base url.
        :param base_url: Base url to append to the url if it is relative.
        :param url: The url to check.
        :return: A definitely valid url.
        :raises Exception: If the base url is not set, but the url is relative.
        """
        if url.startswith("http"):
            # url is already valid
            return url
        else:
            if base_url == "":
                raise Exception('[APPEND BASE URL] The base url is not set. Please check your settings.\n' +
                                'For the recursive navigation, it can be done like this:\n' +
                                'my_configuration.set_recursive_navigation([{"css_selector": "div.m-browse--item>ul>li>a", "base_url_in_case_links_are_relative": "https://www.surgicalholdings.co.uk"}])\n' +
                                'If this error occurs when loading the product page, please use the "set_product_site_link_prefix" method to set the base url for the product pages')
            return base_url + url

    def __get_html_document(self, settings: Settings, url: str) -> str:
        """
        Get the html document from the url.
        :param settings: Used to get the custom headers.
        :param url: The url to get the html document from.
        :return: The html document as a string. (The response.text)
        """

        if (self.__current_milli_time() - self.last_request_timestamp) < settings.get_request_delay():
            time.sleep((settings.get_request_delay() - (self.__current_milli_time() - self.last_request_timestamp)) / 1000)

        # request html document
        response = requests.get(url, headers=settings.get_custom_http_headers(), verify=True)
        if settings.get_verbose_output(): print("           [GET HTML DOCUMENT] website loaded: [" + str(response.status_code) + "] (" + str(len(response.text)) + " bytes) " + url)

        self.statistics["requests"] += 1
        if response.status_code != 200:
            print("           [GET HTML DOCUMENT] [ERROR] Status code: " + str(response.status_code) + " for url: " + url)
            self.statistics["failed_requests"] += 1

        # return html document
        return response.text

    def __get_page_object(self, settings: Settings, url: str):
        """
        Get the beautiful soup object from the url.
        :param settings: Only used in called functions.
        :param url: The url to get the page object from.
        :return: The beautiful soup object.
        """

        return BeautifulSoup(self.__get_html_document(settings, url), features="html.parser")

    def __extract_data_from_html_soup(self, settings: Settings, page_object):
        """
        Extract the data from the html soup object.
        Loops through the settings 'product_data_extraction' and extracts the data from the page object.
        :param settings: Used to get the data extraction settings.
        :param page_object: The beautiful soup object to extract the data from.
        :return: A pandas dataframe with the extracted data.
        """
        got_at_least_something = False
        result = {}
        for data_point in settings.get_product_data_extraction():
            selected = page_object.select_one(data_point.get("css_selector"))
            if selected:
                result[data_point.get("column_name")] = [selected.text]
                got_at_least_something = True
            else:
                print("        [EXTRACT DATA] [WARNING] No data found for: " + data_point.get("column_name") + " with selector: " + data_point.get("css_selector"))
                result[data_point.get("column_name")] = np.nan

        # check if the warning is activated
        if settings.get_warning_tag_if_present():
            if page_object.select_one(settings.get_warning_tag_if_present()):
                if settings.get_verbose_output():
                    print("        [EXTRACT DATA] [WARNING] Warning tag found: " + settings.get_warning_tag_if_present())
                result["warning"] = True
                self.statistics["warnings"] += 1
            else:
                result["warning"] = False

        if not got_at_least_something:
            print("        [EXTRACT DATA] [WARNING] No data found at all.")
            return pd.DataFrame()

        if settings.get_verbose_output(): print("        [EXTRACT DATA] Data extracted: " + str(result))

        return pd.DataFrame(result)

    def __get_product_site(self, settings: Settings, url: str):
        """
        Get the product site and extract the data.
        :param settings: Only used in called functions and for verbose output.
        :param url: The url to get the product site from.
        :return: A pandas dataframe with the extracted data.
        """
        # get the page object
        page_object = self.__get_page_object(settings, url)

        return self.__extract_data_from_html_soup(settings, page_object)

    def __get_single_site(self, settings: Settings, url: str = ""):
        """
        Get a single site and extract the data.
        This is intended to be used for sites with multiple products.
        Sites like some sort of gallery or list of products.
        If not every information can be extracted from the gallery, the product site can be visited.
        But this behavior must be configured.
        :param settings: User settings.
        :param url: The url to get the site from.
        :return: A pandas dataframe with the extracted data.
        """
        # get the page object
        page_object = self.__get_page_object(settings, url)

        # get the elements
        page_elements = page_object.select(settings.get_product_element_css_selector())
        if settings.get_verbose_output():
            if settings.get_product_site_needed():
                print("      [GET SINGLE SITE] Found " + str(len(page_elements)) + " elements on site: " + url + ". Now visiting " + str(len(page_elements)) + " product sites.")
            else:
                print("      [GET SINGLE SITE] Found " + str(len(page_elements)) + " elements on site: " + url + ".")

        # get the data of the elements
        results = []
        if settings.get_product_site_needed():
            # visit the product site for each element
            for element in page_elements:
                # get the link to the product site, append the base url if it is relative, (download page, extract data), and get the data to append to the results
                results.append(self.__get_product_site(settings, self.__append_base_url_if_relative(settings.get_product_site_link_prefix(), element.select_one(settings.get_product_site_link_css_selector()).get("href"))))
        else:
            # extract the data for each element
            for element in page_elements:
                # extract the data from the element
                results.append(self.__extract_data_from_html_soup(settings, element))

        # when a page has no elements, return an empty dataframe, and so on
        if len(results) == 0:
            final = pd.DataFrame()
        elif len(results) == 1:
            final = results[0]
        else:
            final = pd.concat(results)

        if settings.get_verbose_output():
            print("      [GET SINGLE SITE] Found " + str(len(results)) + " results for " + url + ".")

        return final

    def __get_paginated_sites(self, settings: Settings, url: str = ""):
        """
        Get multiple pages from a site.
        This is intended to be used for sites with multiple pages.
        Like a gallery or list of products, with only 20 of XXX elements per page.
        It will loop through the pages and get the data.
        IMPORTANT: If a page x has no data, the loop will stop.
        So every page after page x will not be attempted to load.
        :param settings: User settings.
        :param url: The url to get the pages from.
        :return: A pandas dataframe with the extracted data.
        """
        if settings.get_verbose_output(): print("    [GET MULTIPLE SITES] Getting multiple pages from: " + url)

        # if pages are required, loop through the pages
        if settings.get_pages_required():
            results = []

            for i in range(settings.get_page_start(), settings.get_page_end(), settings.get_page_step()):
                # create the url for the page
                url_to_load = url + settings.get_base_url_paging_prefix() + str(i) + settings.get_base_url_paging_suffix()
                # get the data from the page (not inline, to be able to check if the page is empty)
                page_results = self.__get_single_site(settings, url_to_load)
                # if the page has the same data as the last page, stop the loop
                if len(results) > 0:
                    # cant use an and here, because it will fail with an index out of range error
                    if results[-1].equals(page_results):
                        if settings.get_verbose_output(): print("    [GET MULTIPLE SITES] Found same data as before: " + url_to_load + ". Stopping.")
                        break
                # if the page is empty, stop the loop
                if page_results.empty:
                    if settings.get_verbose_output(): print("    [GET MULTIPLE SITES] No more data found on page: " + url_to_load + ". Stopping.")
                    break
                # append the results
                results.append(page_results)

            # when no results are found, return an empty dataframe
            if len(results) == 0:
                final = pd.DataFrame()
            elif len(results) == 1:
                final = results[0]
            else:
                final = pd.concat(results)

            print("    [GET MULTIPLE SITES] Found " + str(len(final)) + " results on paginated site: " + url + ".")

            return final
        else:
            return self.__get_single_site(settings, url)

    def __get_website(self, settings: Settings):
        """
        Get the website with the settings provided.

        In the first step, it will check if the settings require recursive navigation.
        If there are steps left, it will navigate to the next step (this is recursive).

        If no steps are left, it will get the paginated sites if paging is activated.

        After that, it will get check whether the product site is needed.
        If the product site is needed, it will get the product site and extract the data.
        If the product site is not needed, it will get the data from that site (and page).

        :param settings: You will find more information in the settings class.
        :return: A pandas dataframe with the extracted data.
        """

        if settings.get_verbose_output(): print("  [GET WEBSITE] Getting website: " + settings.get_base_url())

        # need to navigate recursively?
        # steps left?
        if settings.get_recursive_navigation() and len(settings.get_recursive_navigation()) > 0:
            if settings.get_verbose_output(): print("  [GET WEBSITE] Recursive navigation starting. Steps left: " + str(len(settings.get_recursive_navigation())) + " steps.")
            # --------------------------
            # Load the website
            # --------------------------

            # get the page object
            page_object = self.__get_page_object(settings, settings.get_base_url())
            if settings.get_verbose_output(): print("  [GET WEBSITE] Page object of " + str(settings.get_base_url()) + " created. Found " + str(len(str(page_object))) + " chars.")

            # --------------------------
            # Select subpages
            # --------------------------

            # get the first navigation step
            navigation_step = settings.get_recursive_navigation()
            navigation_step = navigation_step[0]

            # get the elements
            page_elements = page_object.select(navigation_step.get("css_selector"))
            if settings.get_verbose_output(): print("  [GET WEBSITE] Found " + str(len(page_elements)) + " elements.")

            # create a list of the urls
            urls = []
            for element in page_elements:
                # check if the url is relative
                new_url = element.get("href")
                new_url = self.__append_base_url_if_relative(navigation_step.get("base_url_in_case_links_are_relative"), new_url)
                urls.append(new_url)
                if settings.get_verbose_output(): print("  [GET WEBSITE] Found url: " + new_url)

            # --------------------------
            # Check blacklisted urls
            # --------------------------
            if settings.get_verbose_output(): print("  [GET WEBSITE] Checking blacklisted urls.")

            cleaned_urls = []

            for i in range(len(urls)):
                if re.match(settings.get_url_blacklist_regex(), urls[i], re.IGNORECASE):
                    if settings.get_verbose_output(): print("  [GET WEBSITE] Blacklisted url discarded: " + urls[i])
                else:
                    cleaned_urls.append(urls[i])

            urls = cleaned_urls

            # --------------------------
            # Recursion, for all urls
            # --------------------------

            results = []

            # for each url, get the website
            for i in range(len(urls)):
                # create a copy of the settings, but with the new base url and the next navigation step
                n_settings = copy.deepcopy(settings)
                n_settings.set_base_url(urls[i])
                n_recursion = copy.deepcopy(settings.get_recursive_navigation())
                n_recursion.pop(0)
                n_settings.set_recursive_navigation(n_recursion)

                # get the website
                results.append(self.__get_website(n_settings))

            result = pd.concat(results)

        else:
            if settings.get_verbose_output(): print("  [GET WEBSITE] Recursive navigation finished or not set.")
            result = self.__get_paginated_sites(settings, settings.get_base_url())

        # count duplicates
        self.statistics["duplicates"] += len(result) - len(result.drop_duplicates())

        # remove duplicates (for obvious reasons)
        result = result.drop_duplicates()

        return result

    def start_scraper(self, run_args: list = [], settings: Settings = Settings()):

        if self.settings == Settings():
            self.settings = settings

        # if no command line arguments are given, the script will run with these settings
        if len(run_args) == 1:
            print("No arguments given. Running with in-code settings. Abort and use -h for help.")

            # --------------------------
            # Place your settings here
            # --------------------------

            self.settings.set_base_url("https://www.surgicalholdings.co.uk/browse-products.html")
            # ...

            # --------------------------
        else:
            self.settings.parse_args(run_args)

        print("[MAIN] Your settings are fully loaded. If you want to use them again, you can use the following JSON:\n")
        print(self.settings.get_settings_json())
        print("\n\n[MAIN] Starting the scraping process.")

        scraping_results = self.__get_website(self.settings)

        if settings.get_output_file_path() != "":
            scraping_results.to_csv(settings.get_output_file_path(), index=False)

        print("[MAIN] Results:")
        print(scraping_results)
        print("[MAIN] Statistics:")
        print(self.statistics)

        return scraping_results
