import datetime
import re

import xbmc
import xbmcaddon


__id__ = 'service.bgmusic'
__addon__ = xbmcaddon.Addon(__id__)


class Service(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.old_volume = 50
        self.idling = False
        self.queued = False

    def is_armed(self):
        if __addon__.getSetting('always_active') == 'true':
            return True
        time = datetime.datetime.now().time()
        start_hr = int(__addon__.getSetting('start_hr'))
        start_min = int(__addon__.getSetting('start_min'))
        if time > datetime.time(start_hr, start_min):
            stop_hr = int(__addon__.getSetting('stop_hr'))
            stop_min = int(__addon__.getSetting('stop_min'))
            if time < datetime.time(stop_hr, stop_min):
                return True
        return False

    def onPlayBackStarted(self):
        if self.idling:
            if self.queued:
                self.queued = False
            else:
                xbmc.log('BGMusic: User started playback, restoring volume')
                self.idling = False
                builtin = "SetVolume(%s)" % self.old_volume
                xbmc.executebuiltin(builtin)

    def onPlayBackStopped(self):
        if self.idling:
            xbmc.log('BGMusic: Playback stopped, restoring volume')
            self.idling = False
            track_volume = __addon__.getSetting('rem_volume_changes') == 'true'
            if track_volume:
                __addon__.setSetting('volume', get_volume())
            builtin = "SetVolume(%s)" % self.old_volume
            xbmc.executebuiltin(builtin)

    def onPlayBackEnded(self):
        if self.idling:
            track_volume = __addon__.getSetting('rem_volume_changes') == 'true'
            if track_volume:
                __addon__.setSetting('volume', get_volume())
            total = xbmc.getInfoLabel('Playlist.Length')
            current = xbmc.getInfoLabel('Playlist.Position')
            if total == current:
                xbmc.log('BGMusic: Playlist finished, restoring volume')
                self.idling = False
                builtin = "SetVolume(%s)" % self.old_volume
                xbmc.executebuiltin(builtin)

    def onQueueNextItem(self):
        if self.idling:
            self.queued = True
            track_volume = __addon__.getSetting('rem_volume_changes') == 'true'
            if track_volume:
                __addon__.setSetting('volume', get_volume())


def get_volume():
    volume_query = '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": { "properties": [ "volume" ] }, "id": 1}'
    result = xbmc.executeJSONRPC(volume_query)
    match = re.search('"volume": ?([0-9]{1,3})', result)
    return int(match.group(1))

xbmc.log('BGMusic: Service starting...')
mon = Service()
threshold = int(float(__addon__.getSetting('threshold')))

while not xbmc.abortRequested:
    current_idle = divmod(int(xbmc.getGlobalIdleTime()), 60)[0]
    if not mon.isPlaying() and (current_idle > threshold) and mon.is_armed():
        mon.idling = True
        mon.old_volume = get_volume()
        new_volume = int(float(__addon__.getSetting('volume')))
        xbmc.log('BGMusic: Setting volume to %s%%' % new_volume)
        builtin = "SetVolume(%s)" % new_volume
        xbmc.executebuiltin(builtin)

        pl = __addon__.getSetting('playlist')
        xbmc.log('BGMusic: Starting playback of %s' % pl)
        mon.play(pl)

        if __addon__.getSetting('shuffle') == 'true':
            shuffle = 'On'
        else:
            shuffle = 'Off'
        xbmc.log('BGMusic: Setting shuffle %s' % shuffle)
        builtin = 'PlayerControl(Random%s)' % shuffle
        xbmc.executebuiltin(builtin)

        repeat = __addon__.getSetting('repeat')
        if not repeat == 'No Change':
            repeat_modes = {'Off': 'RepeatOff', 'One': 'RepeatOne', 'All': 'RepeatAll'}
            xbmc.log('BGMusic: Setting repeat to %s' % repeat)
            builtin = 'PlayerControl(%s)' % repeat_modes[repeat]
            xbmc.executebuiltin(builtin)

    xbmc.sleep(10000)

xbmc.log('BGMusic: Service shutting down...')
