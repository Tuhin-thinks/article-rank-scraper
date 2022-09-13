from typing import Union

from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        InvalidArgumentException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from globals import Driver


class Google:
    def __init__(self):
        self.exe_path = ChromeDriverManager().install()
        self.driver: Union[None, webdriver.Chrome] = None

    def reinit_driver(self):
        self.driver = webdriver.Chrome(self.exe_path)
        Driver.instance = self.driver

    def get_search_links(self, url: str, search_art_videos=True):
        links = []
        titles = []
        # initialize driver if not exists
        if not self.driver:
            self.reinit_driver()
        self.driver.get(url)

        page_link_selector = "div>a"
        a_tags = self.driver.find_elements(By.CSS_SELECTOR, page_link_selector)
        for a_tag in a_tags:
            if a_tag.find_elements(By.CSS_SELECTOR, "h3"):
                title = a_tag.find_element(By.CSS_SELECTOR, "h3").text
                link = a_tag.get_attribute("href")

                links.append(link)
                titles.append(title)

        # all tab video section
        video_links = []
        video_titles = []
        if not search_art_videos:
            return links, titles, video_links, video_titles
        try:
            for _ in range(5):
                self.driver.execute_script("window.scrollBy(0, 500);")

            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "video-voyager")))
            except TimeoutException:
                return links, titles, video_links, video_titles

            video_section_selector = "div[jsname=TFTr6]>div a"
            video_title_selector = "div span.cHaqb"
            video_links = [elem.get_attribute('href') for elem in
                           self.driver.find_elements(By.CSS_SELECTOR,
                                                     video_section_selector)]
            video_titles = [elem.text for elem in
                            self.driver.find_elements(By.CSS_SELECTOR,
                                                      video_title_selector)]
            print(video_links, video_titles)
        except (NoSuchElementException, InvalidArgumentException):
            pass
        self.driver.quit()
        self.driver = None
        return links, titles, video_links, video_titles

    def close_driver(self):
        self.driver.quit()
