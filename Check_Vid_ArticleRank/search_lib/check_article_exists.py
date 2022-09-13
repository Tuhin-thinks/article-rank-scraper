import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse
from .tools import Url
# from . import chrome

google = None


def get_domain(link: str):
    return urlparse(link).hostname


def get_last_updated_info(gfg_page_link: str):
    response = requests.get(gfg_page_link)
    soup = BeautifulSoup(response.content, 'html5lib')
    last_updated_xpath = "div.meta>ul"
    xpath_span_element = soup.select_one(last_updated_xpath)
    return xpath_span_element.text.replace('\n', ''), get_last_improved(soup)


def get_last_improved(soup: BeautifulSoup):
    last_improved_by_css_selector = "div.improved:nth-child(1)>ul>li>a"
    return [x.text for x in soup.find_all(last_improved_by_css_selector)]


def get_search_links(soup):
    anchors = soup.select('div>div>a')
    links = []
    titles = []

    for anchor in anchors:

        if anchor.select("h3"):
            # getting only the hyperlink portion of the attribute
            link_mod = anchor['href']
            try:
                if link_mod[link_mod.index('=') +
                            1:link_mod.index('&')].startswith('https://'):
                    link_ = link_mod[
                            link_mod.index('=') + 1:link_mod.index('&')]
                    if link_ not in links and "support.google.com" not in link_:
                        try:
                            h3 = anchor.findChild().text
                            titles.append(h3)
                            links.append(link_)
                        except AttributeError:
                            # print(link_)
                            continue
            except ValueError:
                pass
    return titles, links


def get_art_vid_links(soup: BeautifulSoup):
    all_anchors = soup.select("a")
    links = []
    titles = []
    for a in all_anchors:
        if soup.select("span.cHaqb"):
            link = a['href']
            title = soup.select_one("span.cHaqb").text
            links.append(link)
            titles.append(title)
    return titles, links


def do_search(search_query, match_url=False, target_url=None,
              custom_url_filter=False, custom_filter_condition=None,
              display=False, dorking_add=None, art_video_search=True):
    global google
    artRank, artTitle, artLink = -1, "", None
    artVidRank, artVidTitle, artVidLink = -1, "", None
    url_pre = "https://www.google.com/search?"

    # search_query = input("Search query: ")
    search_dict = {'q': search_query}
    if dorking_add:
        search_dict.update(dorking_add)
    quoted_query = urlencode(search_dict)

    url = url_pre + quoted_query
    print(url)
    if display:
        print(url)

    # header = {"Accept-Language": "en-US,en;q=0.5",
    #           "user-agent": "Mozilla/5.0 (X11; Linux x86_64) "
    #                         "AppleWebKit/537.36 (KHTML, like Gecko) "
    #                         "Chrome/105.0.0.0 Safari/537.36"}
    # header = {"Accept-Language": "en-US,en;q=0.5"}

    # if not google:
    #     google = chrome.Google()

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # todo: remove this later
    # with open("search-page.html", "wb") as file_writer:
    #     file_writer.write(response.content)

    titles, search_links = get_search_links(soup)
    # search_links, titles, art_vid_links, art_vid_titles = google.get_search_links(url, search_art_videos=art_video_search)

    for art_rank, (art_title, art_link) in enumerate(zip(titles,
                                                         search_links), 1):
        if custom_url_filter and custom_filter_condition(art_link):
            if match_url and Url(art_link) != Url(target_url):
                continue

            if display:
                print(
                    f"\nRank:{art_rank}\nTitle: {art_title}\nLink:{art_link}")

            if art_rank > 1:
                if display:
                    print(f"[Ranking 1-{art_rank - 1} articles]")
                    print("\n".join(search_links[:art_rank - 1]))
            if display:
                print(f"\n{16 * '--'}\n")
            artRank, artTitle, artLink = art_rank, art_title, art_link
            break

    if art_video_search:
        art_vid_titles, art_vid_links = get_art_vid_links(soup)
        for art_vid_rank, (art_vid_title, art_vid_link) in enumerate(
                zip(art_vid_titles, art_vid_links), 1):
            if custom_url_filter and custom_filter_condition(art_vid_link):
                if display:
                    print(
                        f"\nRank:{art_vid_rank}\nTitle: {art_vid_title}\nLink:{art_vid_link}")

                if display:
                    print(f"[Ranking 1-{art_vid_rank - 1} articles]")
                    print("\n".join(art_vid_links[:art_vid_rank - 1]))
                if display:
                    print(f"\n{16 * '--'}\n")
                artVidRank, artVidTitle, artVidLink = art_vid_rank, art_vid_title, art_vid_link
                break
    return artRank, artTitle, artLink, artVidRank, artVidTitle, artVidLink


def main():
    inp_list = []
    while 1:
        inp = input()
        if inp == "END":
            break
        inp_list.append(inp)

    for item in inp_list:
        print(f"Searching {item.strip()}...")
        do_search(item.strip())


if __name__ == '__main__':
    main()
