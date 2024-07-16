"""




python src/fetcher_auto.py test1


"""
import re, time
import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
from utilmy import pd_to_file, pd_read_file, date_now, log



from utils.utilmy_base import (diskcache_decorator )


dirdata="./ztmp/data"


##########################################################################################
def test1():
    urls_list     = ["https://3dprint.com/109310/airbus-autodesk-dividing-wall/amp/"]
    df2, df2_miss = run_fetch(urls_list)
    assert df2[[ "url", "art2_title", "art2_text",       ]].shape
    





##########################################################################################
def clean(xstr):
    return re.sub('\n+', '', re.sub('\s+', ' ', xstr)).strip()


def remove_misc(text):
    MISC_WORDS = ["Articles", "News", "Share", "LinkedIn", "Twitter", "Facebook", "WhatsApp", "Email"]
    for misc in MISC_WORDS :
        text = text.replace(misc, "")

    return text


def url_extract_words(url) :

    # trims last char if it is "/"
    if url.endswith("/") :
        url = url[:-1]

    # get the longest string which is potentially the url title
    word_list = url.split("/")[-1]

    # many urls will have potential keywords list in second last part of it
    if len(url.split("/")[-1]) <  len(url.split("/")[-2]) :
        word_list = url.split("/")[-2]

    # remove words with length less than 5
    word_list = list(filter(lambda ele: len(ele) >= 5, word_list.split("-")))

    return word_list, url


def get_best_content(txt_all, txt_specific, txt_all_sel, txt_sel_specific):
    if (len(txt_all) > 0 and len(txt_specific) > 0) and (len(txt_all) > len(txt_specific)):

        # if there is slight difference (upto 20%) in the text lengths, then it is highly possible that specific tags have got precise core content
        if float(len(txt_specific))/float(len(txt_all)) < 0.2:
            txt, txt_sel = txt_specific, txt_sel_specific
        else:
            txt, txt_sel = txt_all, txt_all_sel

    elif txt_specific != "":
        txt, txt_sel = txt_specific, txt_sel_specific

    else :
        txt, txt_sel = txt_all, txt_all_sel

    return txt, txt_sel


def find_best(text, text_sel, title, title_sel, txt, txt_sel, ttl, ttl_sel, txt_len, ttl_len, word):
    if txt_len < len(text) :
        txt, txt_sel, txt_len = text, text_sel, len(text)

    if title.lower().startswith(word.lower()):
        # this is the title even if anything else has longer length
        ttl, ttl_sel, ttl_len = title, title_sel, 200

    if ttl_len < len(title):
        ttl, ttl_sel, ttl_len = title, title_sel, len(title)

    return txt, txt_sel, txt_len, ttl, ttl_sel, ttl_len



def playw_extract_tag_text(page, elts, word, source):
    max_len, text, text_sel = 0, "", ""

    try :
        for elt in elts:
            # checking if the elt is html elt or not if not isinstance(elt, page._elt_handle_factory.create_js_handle('HTMLelt')._impl), so if goes to except, means elt is not html elt and we should move to next elt in loop
            try :
                elt_text = elt.inner_text()

            except :
                continue

            # skip texts exceeding char len of 230 for potential titles
            if source == "Title" and len(elt_text) > 230:
                continue

            else :
                elt_text = remove_misc(elt_text)

            # check if given word is present in the element text
            if word.lower() in elt_text.lower():
                elt_tag = elt.get_property('tagName').json_value().lower()

                # skip "script" tags
                if elt_tag == "script" :
                    continue

                # check if element is having class attribute present
                elt_classes = None

                if elt.get_attribute("class") :
                    elt_classes = ".".join(elt.get_attribute("class").split())

                elt_sel = f"{elt_tag}.{elt_classes}" if elt_classes else elt_tag

                # prioritize elements with tag=h1, for potential titles over other elements
                if source.strip() == "Title" and elt_tag == "h1":
                    return elt_text, elt_sel

                if max_len < len(elt_text) :
                    text, text_sel, txt_len = elt_text, elt_sel, len(elt_text)

    except Exception as e:
        pass

    return text, text_sel



def playw_cookies(page):
    try:
        # list of possible "accept all cookies" button selectors
        cookie_btn_sel = 'button[title="Accept all"], button[id="onetrust-accept-btn-handler"], a[id="btnSelectAllCheckboxes"], button[aria-label="Accept cookies"], button[id*="cookie"], button[class*="cookie"]'
        if page.is_visible(cookie_btn_sel):
            page.click(cookie_btn_sel)

    except:
        pass


def playw_find_sel_by_text(page, txt):

    playw_cookies(page)

    # find all elts, potential title and potential content elements
    all_elts   = page.query_selector_all("body *")
    title_elts = page.query_selector_all('h1, h2, [class*="heading"], [class*="header"], [class*="title"]')
    txt_elts   = page.query_selector_all('[class*="entry-content"], [class*="articleBody"], [class*="post-content"], [class*="content-body"], [class*="article-body"], [class*="the-content"], [class*="article-content"]')

    # get best title and core text found for the given word from all potential elements
    title, title_sel = playw_extract_tag_text(page, title_elts, txt, "Title")
    txt_specific, txt_sel_specific = playw_extract_tag_text(page, txt_elts, txt, "Core")
    txt_all, txt_all_sel = playw_extract_tag_text(page, all_elts, txt, "Core")

    # choose one core text from "potential selectors" and "all selectors"
    txt, txt_sel = get_best_content(txt_all, txt_specific, txt_all_sel, txt_sel_specific)

    return txt_sel, txt, title_sel, title


@diskcache_decorator
def run_fetch(urls_list, dirout="./ztmp", cols_extract=None):
    """

    """
    cols_extract = [ "url", "art2_date", "art2_title", "art2_text", "info"  ]
    
    dirout = dirdata +'/news_tmp/playw_run_fetch/'
    #fout        = open( dirout + "/extract_all.tsv", "w")
    #fout_miss   = open( dirout + "/extract_miss.tsv", "w")

    fout = []
    fout_miss = []

    # write headers in output files
    # fout.write("\t".join([ "url", "text_sel", "text", "title_sel", "title" ])+"\n")
    # fout_miss.write("\t".join([ "url", "error"]))

    # open browser with playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page    = browser.new_page()

        # parse urls in list, one by one to get the core text and title
        for ii, url1 in enumerate(urls_list) :
            log("fetching:", ii )
            try :
                page.goto(url1)

                word_list, url1 = url_extract_words(url1)

                txt_len, txt, txt_sel = 0, "", ""
                ttl_len, ttl, ttl_sel = 0, "", ""

                for word in word_list:
                    text_sel, text, title_sel, title = playw_find_sel_by_text(page, word)

                    # compare the potential text and title we got for this word, with texts and titles from previous words and update the texts, selectors, max lengths of texts
                    txt, txt_sel, txt_len, ttl, ttl_sel, ttl_len = find_best(text, text_sel, title, title_sel, txt, txt_sel, ttl, ttl_sel, txt_len, ttl_len, word_list[0])
                            
                # write output for every url,
                # fout.write("\t".join([clean(url1), clean(txt_sel), clean(txt), clean(ttl_sel), clean(ttl)])+"\n")
                fout.append([clean(url1), clean(txt_sel), clean(txt), clean(ttl_sel), clean(ttl)] )

            except Exception as e:
                # fout_miss.write(url1+"\t"+clean(str(e))+"\n")
                log(e)
                fout_miss.append( [url1, clean(str(e)) ] )

        browser.close()


    #### Fetched
    fout = pd.DataFrame(fout, 
                        columns = [ "url", "text_sel", "art2_text", "title_sel", "art2_title" ] )

    fout['info'] = fout.apply(lambda x: f"'text-sel':{x['text_sel']};'title_sel':{x['title_sel']}", axis=1)
    fout["art2_date"] = date_now(fmt="%Y/%m/%d")

    fout = fout[ cols_extract ]
    log("\nFetched:\n", fout)
    YMD = date_now(fmt="%y%m%d")
    if len(fout) > 0:
       pd_to_file(fout,      dirout + f'/text/df_text_{YMD}.parquet', show=0)  


    #### Missed 
    fout_miss = pd.DataFrame(fout_miss, columns= [ "url", "err_msg" ] )
    log("\n\nMissed: ", fout_miss)
    if len(fout_miss) > 0:      
       pd_to_file(fout_miss, dirout + f'/miss/df_miss_{YMD}.parquet', show=0)  

    return fout, fout_miss








###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()


