import sys
import string
import urllib
import xml.etree.ElementTree as ET
import json
import re
import HTMLParser

url = urllib.urlopen('http://www.stream.cz/ajax/get_catalogue?dreams')
parser = HTMLParser.HTMLParser()
response = parser.unescape(url.read().decode('UTF-8'))
catalogue = re.findall('<a href="/pohadky/(.*)" class.*data-action="click:menu">\s*(.*)\s*<img src="(.*)" alt', response)

for show_url, show_name, show_image in catalogue:
    print show_url, show_name, show_image

# catalogue = ET.fromstring(response)
#
# for show in catalogue.iter('a'):
#      print show.text
#      print show.attrib['href']

# for show in root.iter('img'):
#     title = show.attrib['title']
#     print show.attrib
#     print title

#
# show_url = 'mach-a-sebestova'
# url = urllib.urlopen('http://www.stream.cz/ajax/get_series?show_url=' + show_url)
# response = url.read()
# episodes = re.findall('data-episode-id="(\d*)"', response)
#
# for episode_id in episodes:
#     quality = 3
#     url = urllib.urlopen('http://www.stream.cz/ajax/get_video_source?context=catalogue&id=' + episode_id)
#     response = url.read()
#     episode = json.loads(response)
#     episode_name = episode['episode_name']
#     episode_source = episode['instances'][quality]['instances'][0]['source']
#     episode_type = episode['instances'][quality]['instances'][0]['type']
#     episode_quality_label = episode['instances'][quality]['instances'][0]['quality_label']
#     episode_quality = episode['instances'][quality]['instances'][0]['quality']
#     episode_image = episode['episode_image_original_url']
#     print episode_name, episode_source, episode_type, episode_quality_label, episode_quality, episode_image

