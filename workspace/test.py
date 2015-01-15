import sys
import string
import urllib
import xml.etree.ElementTree as ET
import json
import re
import HTMLParser

STREAM_URL = 'http://www.stream.cz/API'

url = urllib.urlopen(STREAM_URL + '/catalogue?channels=3')
response = url.read()

try:
    catalogue = json.loads(response)
except ValueError:
    sys.exit()

print len(catalogue['_embedded']['stream:show'])

for show in range(0, len(catalogue['_embedded']['stream:show'])):
    show_url = catalogue['_embedded']['stream:show'][show]['url_name']
    show_name = catalogue['_embedded']['stream:show'][show]['name']
    show_image = catalogue['_embedded']['stream:show'][show]['image']
    print show_url, show_name, show_image


url = urllib.urlopen(STREAM_URL + 'show/jezisek')
response = url.read()

try:
    episodes = json.loads(response)
except ValueError:
    sys.exit()

if isinstance(episodes['_embedded']['stream:season']['_embedded']['stream:episode'], list):
    print len(episodes['_embedded']['stream:season']['_embedded']['stream:episode'])
    for episode in range(0, len(episodes['_embedded']['stream:season']['_embedded']['stream:episode'])):
        episode_id = episodes['_embedded']['stream:season']['_embedded']['stream:episode'][episode]['id']
        print episode_id
else:
    episode_id = episodes['_embedded']['stream:season']['_embedded']['stream:episode']['id']
    print episode_id


show_image = re.findall('.+?(?=/\{width\}/\{height\})', '//im.stream.cz/images/540ab87e84bc715be5640000/{width}/{height}', re.I)
print show_image[0]



# url = urllib.urlopen('http://www.stream.cz/ajax/get_catalogue?dreams')
# parser = HTMLParser.HTMLParser()
# response = parser.unescape(url.read().decode('UTF-8'))
# catalogue = re.findall('<a href="/pohadky/([^"]+)[^>]*>\s*(.*)\s*.*(?=<img)<img src="([^"]+)', response, re.I)
#
# for show_url, show_name, show_image in catalogue:
#     print show_url, show_name, show_image

# catalogue = ET.fromstring(response)
#
# for show in catalogue.iter('a'):
#      print show.text
#      print show.attrib['href']

# for show in root.iter('img'):
#     title = show.attrib['title']
#     print show.attrib
#     print title


# show_url = 'sam-sam'
# url = urllib.urlopen('http://www.stream.cz/ajax/get_series?show_url=' + show_url)
# response = url.read()
# episodes = re.findall('data-episode-id="(\d*)"', response)
#
# for episode_id in episodes:
#     quality = 3
#     #print 'http://www.stream.cz/ajax/get_video_source?context=catalogue&id=' + episode_id
#     url = urllib.urlopen('http://www.stream.cz/ajax/get_video_source?context=catalogue&id=' + episode_id)
#     response = url.read()
#     try:
#         episode = json.loads(response)
#     except ValueError:
#         print 'error'
#         sys.exit()
#     episode_name = episode['episode_name']
#     episode_source = episode['instances'][quality]['instances'][0]['source']
#     episode_type = episode['instances'][quality]['instances'][0]['type']
#     episode_quality_label = episode['instances'][quality]['instances'][0]['quality_label']
#     episode_quality = episode['instances'][quality]['instances'][0]['quality']
#     episode_image = episode['episode_image_original_url']
#     #print episode_name, episode_source, episode_type, episode_quality_label, episode_quality, episode_image
#     print episode_name, episode_source
