import re
import logging
import datetime
import time

from argparse import ArgumentParser
from concurrent import futures
import contextlib

import urllib.request
import urllib.error
from urllib.parse import quote

from linker_finder import LinkerFinder


black_list = None
domain = None
keyword = None
gl_url_cache = set()

logging.basicConfig(filename="./dist/error.log", level=logging.INFO)


def file_to_arr(path):
    result = []

    if path is not None:
        with open(path) as f:
            result = f.read().splitlines()

    return result


def main(args):
    global black_list
    global keyword
    global domain

    cache = []

    black_list = file_to_arr(args.black)
    keyword = args.keyword
    extract = args.extract
    delay_time = int(args.delay)
    domain = args.domain

    if extract is not None:
        if extract == "false":
            extract_result = result_extract("False")
            write_to_extract(extract_result)

        elif extract == "true":
            extract_result = result_extract("True")
            write_to_extract(extract_result)

        else:
            print("expect input value should be false or true")

        return

    if keyword is None:
        print("No keyword input")
        return

    cache.append(args.url)
    result = url_parser_control(cache)

    while len(result) > 0:
        time.sleep(delay_time)
        print("======== sleep end, next iteration ========\n")
        result = url_parser_control(result)


def result_extract(flag):
    with open("./dist/result") as f:
        lines = f.readlines()
        for line in lines:
            line_split = line.split(" ")
            if flag in line_split[1]:
                yield line_split[0]


def url_parser_control(cache):
    if len(cache) is 0:
        return

    result = []
    cache = check_in_black(cache)

    i = 0
    c = 100
    l = len(cache)

    print(f"HINT: total {l} urls need to be processed")

    while c < l:
        temp_cache = url_parser_batch(cache[i:c])
        i = c
        c = c + 100
        result.extend(temp_cache)

    if c != l:
        temp_cache = url_parser_batch(cache[i:l])
        result.extend(temp_cache)

    return result


def url_parser_batch(batch):
    l = len(batch)
    global gl_url_cache
    temp_cache = []
    result = []

    with contextlib.closing(futures.ThreadPoolExecutor()) as executor:
        http_results = executor.map(processor, batch)
        for res in http_results:
            if res[0] is not None:
                continue

            for url in res[1].cache:
                if url in gl_url_cache:
                    continue

                gl_url_cache.add(url)
                temp_cache.append(url)

            result.append((res[1].url, res[1].existed))

        print(f"HINT: {l} urls have been processed")

    write_to_result(result)
    return temp_cache


def write_to_extract(data):
    dt = datetime.datetime.now()
    str_dt = dt.strftime("%s")
    with open(f"./dist/extract_{str_dt}", "w+", encoding="utf8") as f:
        f.writelines("%s\n" % l for l in data)
    f.close()


def write_to_result(data):
    with open("./dist/result", "a", encoding="utf8'") as f:
        f.write("\n".join("{} {}".format(x[0], x[1]) for x in data))
    f.close()


def check_in_black(cache):
    global black_list

    if len(black_list) is 0:
        return cache

    result = []
    for c in data:
        if any(s in c for s in black_list):
            continue

        result.append(c)

    return result


def processor(url):
    global keyword
    global domain

    try:
        s = quote(url, safe="/:?=-", encoding="utf8")
        response = urllib.request.urlopen(s)
        html_response = response.read()
        encoding_html = response.headers.get_content_charset("utf8")
        decoded_html = html_response.decode(encoding_html, errors="ignore")

        parser = LinkerFinder(keyword, url, domain)
        parser.feed(decoded_html)

    except urllib.error.HTTPError as err:
        logging.info(url)
        logging.error(str(err.code))
        return err, None

    except Exception as e:
        logging.info(url)
        logging.error(str(e))
        return e, None

    return None, parser


if __name__ == "__main__":
    parser = ArgumentParser(description="Utilty tool to check embeded code")
    parser.add_argument("-u", help="url to start", dest="url", default=None)
    parser.add_argument("-b", help="black list path", dest="black", default=None)
    parser.add_argument("-k", help="keyword", dest="keyword", default=None)
    parser.add_argument("-e", help="extract result", dest="extract", default=None)
    parser.add_argument("-t", help="delay time", dest="delay", default=10)
    parser.add_argument("-d", help="domain", dest="domain", default=None)

    args = parser.parse_args()
    main(args)
