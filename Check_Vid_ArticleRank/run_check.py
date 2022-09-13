import os
from datetime import datetime
import hashlib
import time
import traceback
from urllib.parse import urlparse
from .search_lib.check_article_exists import do_search
import pandas as pd
from .globals import Driver

if not os.path.exists("downloads"):
    os.mkdir("downloads")


def url_filter_condition(url: str):
    parse_object = urlparse(url)
    path_string = parse_object.path
    split_section = path_string.split("/", 2)[1]
    if split_section.lower() == "videos" and parse_object.hostname == "www.geeksforgeeks.org":
        return True
    else:
        return False


def query(title: str):
    # do search for article
    article_rank, article_title, article_link, art_video_rank, art_video_title, art_video_link = do_search(
        title,
        custom_url_filter=True,
        custom_filter_condition=url_filter_condition)
    # do same search but for video
    vid_rank, vid_title, vid_link, _, _, _ = do_search(
        title,
        custom_url_filter=True,
        custom_filter_condition=url_filter_condition,
        dorking_add={"tbm": "vid"},
        art_video_search=False)
    return (article_rank, article_title, article_link, art_video_rank,
            art_video_title, art_video_link, vid_rank, vid_title, vid_link)


def driver(file_name=None):
    print("Am here")
    links_df = pd.read_csv(file_name)
    start_time = time.perf_counter()
    all_columns = ['[All TAB] Article Rank', "[All TAB] Video Rank",
                   "[All TAB] Article Matched title", "[Video TAB] Video Rank",
                   "[Video TAB] Video Title",
                   "[Links] All_Tab-All_Tab_Video-Video_Tab"]
    for col in all_columns:
        links_df[col] = None
    # ------------------ CONFIGURATION PARAMETERS ----------------------
    # set to min size
    start_count = 0  # including
    # set to max size
    end_count = links_df.shape[0]  # excluding
    # -----------------------------------------------------------------
    count = 0
    try:
        for index, row in links_df.iterrows():
            if start_count <= count < end_count:
                pass
            else:
                continue
            search_query = row['Title']
            print(f'{"--" * 16}\n'
                  f'Searching: {search_query}')
            article_rank, article_title, article_link, art_video_rank, \
            art_video_title, art_video_link, vid_rank, vid_title, vid_link = query(
                search_query)
            if article_rank != -1:
                print('FOUND', article_rank)
            else:
                print("NOT FOUND")
                article_rank = "NA"
            if art_video_rank != -1:
                print("ARTICLE TAB VIDEO FOUND")
            else:
                print("NO ARTICLE TAB VIDEOS")
            if vid_rank != -1:
                print('VIDEO FOUND', vid_rank)
            else:
                print("VIDEO NOT FOUND")
                vid_rank = "NA"

            print("--" * 16)
            all__links = "\n".join([str(__link or "N/A")
                                    for __link in (article_link,
                                                   art_video_link,
                                                   vid_link)])
            row[all_columns] = [article_rank, art_video_rank, article_title,
                                vid_rank, vid_title, all__links]
            count += 1
    except Exception as err:
        print("Script stopped due to error:", err.__str__())
        traceback.print_exc()

    end_time = time.perf_counter()
    time_diff = end_time - start_time
    print(f"Time taken: {time_diff:.03f}sec. ({time_diff / 60:.02f}mins.)")
    time_hash = hashlib.md5(datetime.now().isoformat().encode("utf-8")).hexdigest()
    op_file = os.path.join("downloads", f"Results_{time_hash}.csv")
    links_df.to_csv(op_file)
    try:
        Driver.instance.quit()
    except:
        pass
    return op_file


if __name__ == '__main__':
    driver(file_name="Video_Search_List.csv")
