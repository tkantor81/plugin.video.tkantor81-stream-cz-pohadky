import xbmcgui
import xbmcplugin

import sys
import urllib
import urlparse
import re
import json
import HTMLParser

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

# TODO: create notifications for newly added shows

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

if mode is None:
    url = urllib.urlopen('http://www.stream.cz/ajax/get_catalogue?dreams')
    parser = HTMLParser.HTMLParser()
    response = parser.unescape(url.read().decode('UTF-8'))

    # TODO: do it more general
    catalogue = re.findall('<a href="/pohadky/(.*)" class.*data-action="click:menu">\s*(.*)\s*<img src="(.*)" alt', response)

    for show_url, show_name, show_image in catalogue:
        url = build_url({'mode': 'show', 'show_url': show_url})
        li = xbmcgui.ListItem(show_name, iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
        # TODO: process show images

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'show':
    show_url = args['show_url'][0]
    url = urllib.urlopen('http://www.stream.cz/ajax/get_series?show_url=' + show_url)
    response = url.read()
    episodes = re.findall('data-episode-id="(\d*)"', response, re.I)

    # TODO: add to settings
    quality = 3

    for episode_id in episodes:
        url = urllib.urlopen('http://www.stream.cz/ajax/get_video_source?context=catalogue&id=' + episode_id)
        response = url.read()
        episode = json.loads(response)
        episode_name = episode['episode_name']
        episode_source = episode['instances'][quality]['instances'][0]['source']
        episode_type = episode['instances'][quality]['instances'][0]['type']
        episode_quality_label = episode['instances'][quality]['instances'][0]['quality_label']
        episode_quality = episode['instances'][quality]['instances'][0]['quality']
        episode_image = episode['episode_image_original_url']

        li = xbmcgui.ListItem(episode_name, iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=episode_source, listitem=li)
        # TODO: process episode metadata and images

    xbmcplugin.endOfDirectory(addon_handle)