from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from utils.request import get_logger, get_player_db, get_ini_dict

async def update_player_layout(request: Request, custom_logger=Depends(get_logger), player_db=Depends(get_player_db), ini_dict=Depends(get_ini_dict)):
    data = await request.json()
    layout = data.get("layout")
    
    if layout == 'img1':
        num_players = 1
    elif layout == 'img2':
        num_players = 4
    elif layout == 'img3':
        num_players = 9
    elif layout == 'img4':
        num_players = 16
    else:
        num_players = 1

    all_players = player_db.get_all_devices()
    all_players.sort(key=lambda p: p.idx)
    
    for i, player in enumerate(all_players):
        if i < num_players:
            player_db.update_device(player.idx, {'channel_id': player.channel_id})
        else:
            player_db.update_device(player.idx, {'channel_id': None})

    return JSONResponse(content={"detail": "Player layout updated successfully"})
