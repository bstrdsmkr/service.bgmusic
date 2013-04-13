import xbmc
import datetime
import xbmcaddon

__id__ = 'service.bgmusic'
__addon__ = xbmcaddon.Addon(__id__)

class Service(xbmc.Player):
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
    
    def is_armed(self):
        if __addon__.getSetting('always_active')=='true':
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
                

    
    
mon = Service()
threshold = int(__addon__.getSetting('threshold'))

while not xbmc.abortRequested:
    current_idle = divmod(int(xbmc.getGlobalIdleTime()), 60)[0]
    if not mon.isPlaying() and (current_idle > threshold) and mon.is_armed():
        # volume_query = '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": { "properties": [ "volume" ] }, "id": 1}'
        # result = xbmc.executeJSONRPC( volume_query )
        # match = re.search( '"volume": ?([0-9]{1,3})', result )
        # self.old_volume = int( match.group(1) )
        new_volume = int(__addon__.getSetting('volume'))
        builtin = "SetVolume('%s')" %new_volume
        xbmc.executebuiltin(builtin)

        pl = __addon__.getSetting('playlist')
        mon.play(pl)
        
        if __addon__.getSetting('shuffle')=='true': shuffle = 'On'
        else: shuffle = 'Off'
        builtin = 'PlayerControl(Random%s)' %shuffle
        xbmc.executebuiltin(builtin)
        
        repeat = __addon__.getSetting('repeat')
        repeat_modes = {'Off':'RepeatOff', 'One':'RepeatOne', 'All':'RepeatAll'}
        builtin = 'PlayerControl(%s)' %repeat_modes[repeat]
        xbmc.executebuiltin(builtin)
    
    xbmc.sleep(10000)

