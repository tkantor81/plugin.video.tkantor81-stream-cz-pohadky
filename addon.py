#    XBMC Plugin Add-on: Stream.cz - Pohadky
#    Copyright (C) 2014  tkantor81 (tkantor81@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import sys
import urllib
import urlparse
import re
import json


ADDON_ID = 'plugin.video.tkantor81-stream-cz-pohadky'
STREAM_URL = 'http://www.stream.cz/API/'
NOTIFY_DURATION = 5000


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
my_addon_name = my_addon.getAddonInfo('name')
my_addon_icon = my_addon.getAddonInfo('icon')
level = args.get('level', None)
xbmcplugin.setContent(addon_handle, 'movies')

if level is None:
    url = urllib.urlopen(STREAM_URL + 'catalogue?channels=3')
    response = url.read()

    try:
        catalogue = json.loads(response)
    except ValueError:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (my_addon_name, my_addon.getLocalizedString(30010).encode('UTF-8'), NOTIFY_DURATION, my_addon_icon))
        xbmc.executebuiltin('ReplaceWindow(Home)')
        sys.exit()

    for show in range(0, len(catalogue['_embedded']['stream:show'])):
        show_url = catalogue['_embedded']['stream:show'][show]['url_name']
        show_name = catalogue['_embedded']['stream:show'][show]['name']
        show_image = re.findall('.+?(?=/\{width\}/\{height\})', catalogue['_embedded']['stream:show'][show]['image'], re.I)

        url = build_url({'level': 'show', 'show_url': show_url, 'mode': ShowMode.LIST_EPISODES})
        li = xbmcgui.ListItem(show_name, iconImage='DefaultFolder.png')
        li.setThumbnailImage('http:' + show_image[0])
        li.addContextMenuItems([(my_addon.getLocalizedString(30008), 'RunPlugin(%s)' % build_url({'level': 'show', 'show_url': show_url, 'mode': ShowMode.PLAY_ALL})),
                                (my_addon.getLocalizedString(30009), 'RunPlugin(%s)' % build_url({'level': 'show', 'show_url': show_url, 'mode': ShowMode.SHUFFLE_PLAY}))])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

elif level[0] == 'show':
    mode = int(args['mode'][0])
    if mode == ShowMode.PLAY_ALL:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (my_addon_name, my_addon.getLocalizedString(30008).encode('UTF-8'), NOTIFY_DURATION, my_addon_icon))
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    elif mode == ShowMode.SHUFFLE_PLAY:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (my_addon_name, my_addon.getLocalizedString(30009).encode('UTF-8'), NOTIFY_DURATION, my_addon_icon))
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

    show_url = args['show_url'][0]
    url = urllib.urlopen(STREAM_URL + 'show/' + show_url)
    response = url.read()

    try:
        episodes = json.loads(response)
    except ValueError:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (my_addon_name, my_addon.getLocalizedString(30011).encode('UTF-8'), NOTIFY_DURATION, my_addon_icon))
        xbmc.executebuiltin('RunPlugin(%s)' % base_url)
        sys.exit()

    # settings (0=Very low, 1=Low, 2=Medium, 3=High, 4=Full HD)
    quality = int(my_addon.getSetting('quality'))
    thumbnails = my_addon.getSetting('download_ep_thumbnails')

    for episode in range(0, len(episodes['_embedded']['stream:season']['_embedded']['stream:episode'])):
        episode_id = episodes['_embedded']['stream:season']['_embedded']['stream:episode'][episode]['id']
        url = urllib.urlopen(STREAM_URL + 'episode/' + str(episode_id))
        response = url.read()

        try:
            episode = json.loads(response)
        except ValueError:
            continue

        episode_found = False
        for episode_quality in range(quality, -1, -1):
            if episode['video_qualities'][episode_quality]['formats']:
                episode_found = True
                break

        if episode_found:
            episode_name = episode['name']
            episode_url = episode['video_qualities'][episode_quality]['formats'][0]['source']

            li = xbmcgui.ListItem(episode_name, iconImage='DefaultVideo.png')
            if thumbnails == 'true':
                episode_image = re.findall('.+?(?=/\{width\}/\{height\})', episode['image'], re.I)
                li.setThumbnailImage('http:' + episode_image[0])

            if mode == ShowMode.PLAY_ALL or mode == ShowMode.SHUFFLE_PLAY:
                playlist.add(url=episode_url, listitem=li)
            else:
                episode_type = episode['video_qualities'][episode_quality]['formats'][0]['type']
                episode_aspect = episode['aspect_ratio']
                episode_height = episode['video_qualities'][episode_quality]['formats'][0]['quality'][:3]
                episode_duration = episode['duration']

                li.addStreamInfo('video', {'codec': episode_type, 'aspect': episode_aspect, 'height': episode_height, 'duration': episode_duration})
                li.addStreamInfo('audio', {'language': 'cs'})

                xbmcplugin.addDirectoryItem(handle=addon_handle, url=episode_url, listitem=li)

    if mode == ShowMode.PLAY_ALL:
        xbmc.Player().play(playlist)
    elif mode == ShowMode.SHUFFLE_PLAY:
        playlist.shuffle()
        xbmc.Player().play(playlist)

xbmcplugin.endOfDirectory(addon_handle)