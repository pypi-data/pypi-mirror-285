# creating deep copys of objects
import copy
# for command line arguments
# http(s) requests
import requests
# parsing html
from bs4 import BeautifulSoup
# regex for the regex blacklist
import re
# managing settings
from configuration import Settings
# storing data
import pandas as pd
# just to make something NaN
import numpy as np
# for request delay
import time


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
