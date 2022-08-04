#!/usr/bin/python

from lxml import html
import requests
import re
import os
import urllib.request
import argparse

CHAPTERS_XPATH = '//ul[@class="row-content-chapter"]/li/a/@href'
IMAGES_XPATH = '//div[@class="container-chapter-reader"]/img/@src'
MANGA_XPATH = '//div[@class="story-info-right"]/h1/text()'


def get_page_html(page_url):
    page_source = requests.get(page_url)
    page_source = html.fromstring(page_source.content)
    return page_source


def get_chapters_links(page_source):
    chapters = page_source.xpath(CHAPTERS_XPATH)
    chapters.reverse()
    return chapters


def get_all_images(chapters):
    images_list = {}
    chapter_pattern = re.compile(r'chapter-\d+')
    for chapter in chapters:
        chapter_name = chapter_pattern.search(str(chapter))
        images_source = get_page_html(chapter)
        images = images_source.xpath(IMAGES_XPATH)
        images_list.update({chapter_name.group(): images})
    return images_list


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url", help="url for downloading manga")
    args = p.parse_args()

    manga_content = get_page_html(args.url)
    manga_chapters = get_chapters_links(manga_content)
    manga_images = get_all_images(manga_chapters)
    manga_name = manga_content.xpath(MANGA_XPATH)
    manga_dir_name = str(manga_name[0]).lower().replace(' ', '_')

    opener = urllib.request.build_opener()
    opener.addheaders = [('Referer', 'https://readmanganato.com/')]
    urllib.request.install_opener(opener)

    download_path = os.path.join(os.getcwd(), manga_dir_name)
    os.makedirs(download_path, exist_ok=True)
    print(f'Downloading {manga_name[0]} to {download_path}...')

    for chapter, image_urls in manga_images.items():
        chapter_path = os.path.join(download_path, chapter)
        os.makedirs(chapter_path, exist_ok=True)

        for image_url in image_urls:
            image_name = os.path.basename(image_url)
            image_location = os.path.join(chapter_path, image_name)
            print(f'GET {image_url}')
            urllib.request.urlretrieve(image_url, image_location)

    print(f'Done! {manga_name[0]} has been downloaded successesfully!')


if __name__ == "__main__":
    main()
