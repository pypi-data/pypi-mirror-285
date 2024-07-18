import re

from commmons import get_host_url, html_from_url
from lxml import html
from pydash import head
from commmons import md5

HREF_REGEX = r"\/watch\/([^\/]*)"
THUMBNAIL_REGEX = r"url\(\/\/(.*)\);"


def get_thumbnail_url(atag):
    thumb_div = head(atag.xpath(".//div[@class='img-overflow']"))
    if thumb_div is not None:
        match = re.findall(THUMBNAIL_REGEX, thumb_div.attrib.get("style"))
        return head(match)


def scrape_incflix(url: str, html_body: str):
    host_url = get_host_url(url)
    if html_body:
        root = html.fromstring(html_body)
    else:
        root = html_from_url(url)

    atags = root.xpath("//a[@id='videolink']")

    for atag in atags or []:
        href = atag.attrib.get("href")
        post_id = md5(head(re.findall(HREF_REGEX, href)))
        title = head(atag.xpath(".//span"))
        if title is not None:
            title = title.text
            yield {
                "fileid": "incflix-" + post_id,
                "sourceurl": host_url + href,
                "filename": title,
                "thumbnailurl": get_thumbnail_url(atag)
            }
