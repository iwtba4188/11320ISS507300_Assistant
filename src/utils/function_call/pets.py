# import json
# import random
# import time
# from collections import defaultdict

import pandas as pd

# from selenium.webdriver.common.by import By
# from seleniumbase import SB, Driver
# from utils.helpers import mock_return, read_file_content
from utils.helpers import mock_return

# from .wordcloud import build_word_freq_dict, draw_wordcloud_cat, test_md_draw_wordcloud
from .wordcloud import build_word_freq_dict, test_md_draw_wordcloud

# Dcard URL for "送養" topic
ADOPTION_TAG_URL = "https://www.dcard.tw/topics/%E9%80%81%E9%A4%8A"


def mock_crawling_dcard_urls(target_url_num: int = 10) -> list[tuple[str, str]]:
    res = pd.read_csv("./src/static/article_contents.csv")
    # res = pd.read_csv("../../static/article_contents.csv")
    res = res[["title", "url"]].values.tolist()
    res = [tuple(x) for x in res][:target_url_num]

    return res


@mock_return(result=mock_crawling_dcard_urls)
def cawling_dcard_urls(
    # target_url: str = TARGET_URL,
    target_url_num: int = 3,
) -> list[tuple[str, str]] | None:
    """
    Crawls the urls in Dcard for posts related to pet adoption.

    Args:
        target_url_num (int): The number of URLs to retrieve. Default is 3.

    Returns:
        list[tuple[str, str]] | None: A list of tuples containing the title and URL of each post.
                                      Returns None if an error occurs.
    """
    pass
    # target_url = ADOPTION_TAG_URL

    # try:
    #     driver = Driver(uc=True, headless2=True)
    #     driver.uc_open_with_reconnect(target_url, reconnect_time=3, uc_subprocess=False)
    #     driver.save_screenshot("dcard1.png")
    #     article_section = driver.find_element(
    #         "xpath", '//*[@id="__next"]/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div'
    #     )
    # except Exception as e:
    #     driver.save_screenshot("dcard.png")
    #     raise RuntimeError(f"Error initializing Chrome driver: {e}") from e

    # get_url_num = 0
    # scroll_height = 0
    # url_result = []
    # while get_url_num < target_url_num:
    #     try:
    #         # Scroll down to load more posts
    #         driver.execute_script(f"window.scrollTo(0, {scroll_height});")
    #         time.sleep(2)  # Wait for new posts to load

    #         # Find all post elements
    #         post_elements = article_section.find_elements(
    #             By.CLASS_NAME,
    #             "d_d8_1hcvtr6.d_cn_2h.d_gk_10yn01e.d_7v_gdpa86.d_1938jqx_2k.d_2zt8x3_1y.d_grwvqw_gknzbh.d_1ymp90q_1s.d_89ifzh_1s.d_1hh4tvs_1r.d_1054lsl_1r.t1gihpsa",
    #         )

    #         for ele in post_elements:
    #             post_url = ele.get_attribute("href")
    #             title = ele.text

    #             if post_url not in url_result:
    #                 url_result.append((title, post_url))
    #                 get_url_num += 1

    #         if get_url_num >= target_url_num:
    #             break
    #     except Exception as e:
    #         raise RuntimeError(f"Error retrieving post elements: {e}") from e
    #     finally:
    #         driver.quit()

    #     scroll_height += random.randint(300, 600)

    # print(f"Retrieved {url_result} URLs.")

    # return url_result[:target_url_num]


def mock_crawling_dcard_article_content(target_url: list[str]) -> list[dict]:
    article_data = pd.read_csv("./src/static/article_contents.csv")
    # res = pd.read_csv("../../static/article_contents.csv")

    res = []
    for url in target_url:
        row = article_data.loc[
            article_data["url"] == url, ["title", "author", "createdAt", "content"]
        ].iloc[0]
        res.append(row.to_dict())

    return res


@mock_return(result=mock_crawling_dcard_article_content)
def crawling_dcard_article_content(target_url: list[str]) -> list[dict] | None:
    """
    Crawls the content of a specific Dcard post.

    Args:
        target_url (list[str]): The URL of the Dcard post to crawl.

    Returns:
        list[dict] | None: A dictionary containing the post's title, author, creation date,
                        and content. Returns None if an error occurs.
    """
    pass
    # try:
    #     driver = Driver(uc=True, headless=True)
    # except Exception as e:
    #     driver.save_screenshot("dcard.png")
    #     raise RuntimeError(f"Error initializing Chrome driver: {e}") from e

    # results = []
    # for url in target_url:
    #     driver.uc_open_with_reconnect(url, reconnect_time=3)
    #     result = defaultdict(str)
    #     result["url"] = target_url

    #     try:
    #         result["title"] = driver.find_element("tag name", "h1").text
    #         result["author"] = driver.find_element(
    #             "class name", "d_xa_2b.d_tx_2c.d_lc_1u.d_7v_5.a6buno9"
    #         ).text
    #         result["createdAt"] = driver.find_element("tag name", "time").get_attribute(
    #             "datetime"
    #         )

    #         content_element = driver.find_element(
    #             "class name", "d_xa_34.d_xj_2v.c1ehvwc9"
    #         )
    #         result["content"] = content_element.text
    #         results.append(result)
    #     except Exception as e:
    #         raise RuntimeError(f"Error retrieving post content: {e}") from e

    # return results


def content_wordcloud(contents: list[str]) -> str:
    """
    Generates a word cloud from the content of a str or a list of str.

    Args:
        mode (Literal["cat", "normal", None]): The mode for generating the word cloud.
                                                "cat" for cat-shaped word cloud,
                                                "normal" for normal word cloud,
                                                None for default behavior.

    Returns:
        str: A html image string of the generated word cloud.
    """
    # mode = None
    # urls = cawling_dcard_urls()

    # contents = []
    # for url in urls[:10]:
    #     contents.append(crawling_dcard_article_content(url[1])["content"])

    word_freq = build_word_freq_dict(contents)

    # if mode == "cat":
    #     res = draw_wordcloud_cat(word_freq)
    # elif mode == "normal" or mode is None:
    res = test_md_draw_wordcloud(word_freq)

    return res


# def test_cawling_dcard_urls() -> None:
#     with SB(uc=True, test=True, locale="en", headless=True) as sb:
#         url = "https://www.dcard.tw/f/nthu/p/258754776"
#         sb.activate_cdp_mode(url)
#         # sb.uc_gui_click_captcha()
#         sb.save_screenshot("dcardddddddd.png")
#         sb.sleep(2)


# if __name__ == "__main__":
#     # Example usage
#     # urls = cawling_dcard_urls()
#     # if urls:
#     #     for title, url in urls:
#     #         print(f"Title: {title}, URL: {url}")

#     #     res = crawling_dcard_article_content(urls[0][1])
#     #     print(res)
#     # else:
#     #     print("Failed to retrieve URLs.")

#     mock_urls = mock_crawling_dcard_urls()
#     print(f"{mock_urls=}")

#     mock_res = mock_crawling_dcard_article_content(target_url=mock_urls[0][1])
#     print(f"{mock_res=}")
