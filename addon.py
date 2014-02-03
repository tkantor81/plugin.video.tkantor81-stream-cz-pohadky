import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import sys
import urllib
import urlparse
import re
import json
import HTMLParser

ADDON_ID = 'plugin.video.tkantor81-stream-cz-pohadky'


class ShowMode(object):
    LIST_EPISODES = 0
    PLAY_ALL = 1
    SHUFFLE_PLAY = 2


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

my_addon = xbmcaddon.Addon(ADDON_ID)
level = args.get('level', None)
xbmcplugin.setContent(addon_handle, 'movies')

# TODO: create notifications for newly added shows (configurable)

if level is None:
    url = urllib.urlopen('http://www.stream.cz/ajax/get_catalogue?dreams')
    parser = HTMLParser.HTMLParser()
    response = parser.unescape(url.read().decode('UTF-8'))

    catalogue = re.findall('<a href="/pohadky/([^"]+)[^>]*>\s*(.*)\s*.*(?=<img)<img src="([^"]+)', response, re.I)
    # TODO: notify if catalogue is empty and exit plugin

    for show_url, show_name, show_image in catalogue:
        url = build_url({'level': 'show', 'show_url': show_url, "mode": ShowMode.LIST_EPISODES})
        li = xbmcgui.ListItem(show_name, iconImage='DefaultFolder.png')
        li.setThumbnailImage('http:' + show_image)
        li.addContextMenuItems([(my_addon.getLocalizedString(30006), 'XBMC.RunPlugin(%s)' % build_url({"level": "show", "show_url": show_url, "mode": ShowMode.PLAY_ALL})),
                                (my_addon.getLocalizedString(30007), 'XBMC.RunPlugin(%s)' % build_url({"level": "show", "show_url": show_url, "mode": ShowMode.SHUFFLE_PLAY}))])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

elif level[0] == 'show':
    show_url = args['show_url'][0]
    mode = int(args['mode'][0])
    url = urllib.urlopen('http://www.stream.cz/ajax/get_series?show_url=' + show_url)
    response = url.read()

    episodes = re.findall('data-episode-id="(\d+)"', response, re.I)
    # TODO: notify if episodes are empty and exit to catalogue

    # settings (0=Low, 1=Medium, 2=High)
    quality = int(my_addon.getSetting('quality')) + 1

    if mode == ShowMode.PLAY_ALL or mode == ShowMode.SHUFFLE_PLAY:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

    for episode_id in episodes:
        url = urllib.urlopen('http://www.stream.cz/ajax/get_video_source?context=catalogue&id=' + episode_id)
        response = url.read()

        episode = json.loads(response)
        # TODO: notify if episode(json) is not load properly and exit to catalogue

        episode_name = episode['episode_name']
        episode_url = episode['instances'][quality]['instances'][0]['source']
        episode_type = episode['instances'][quality]['instances'][0]['type']
        episode_height = episode['instances'][quality]['instances'][0]['quality'][:3]
        episode_duration = episode['duration']
        episode_aspect = episode['aspect_ratio']

        li = xbmcgui.ListItem(episode_name, iconImage='DefaultVideo.png')
        li.addStreamInfo('video', {'codec': episode_type, 'aspect': episode_aspect, 'height': episode_height, 'duration': episode_duration})
        li.addStreamInfo('audio', {'language': 'cs'})
        if my_addon.getSetting('download_ep_thumbnails') == 'true':
            episode_image = 'http:' + episode['episode_image_original_url'] + '.jpg'
            li.setThumbnailImage(episode_image)

        if mode == ShowMode.PLAY_ALL or mode == ShowMode.SHUFFLE_PLAY:
            playlist.add(url=episode_url, listitem=li)
        else:
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=episode_url, listitem=li)

    if mode == ShowMode.PLAY_ALL:
        xbmc.Player().play(playlist)
    elif mode == ShowMode.SHUFFLE_PLAY:
        playlist.shuffle()
        xbmc.Player().play(playlist)

xbmcplugin.endOfDirectory(addon_handle)