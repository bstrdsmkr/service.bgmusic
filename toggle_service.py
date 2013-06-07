import xbmc

cmd =  '{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", '
cmd += '"params": { "addonid": "script.bgmusic", "enabled": "toggle" }, "id": 1}'
xbmc.executeJSONRPC(cmd)