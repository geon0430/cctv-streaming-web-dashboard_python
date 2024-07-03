from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from utils.request import get_logger, get_player_db, get_ini_dict
from rtsp import ffprobe

def format_ranges(numbers):
    if not numbers:
        return ""
    
    ranges = []
    start = numbers[0]
    end = numbers[0]

    for num in numbers[1:]:
        if num == end + 1:
            end = num
        else:
            if start == end:
                ranges.append(f"{start}")
            else:
                ranges.append(f"{start}-{end}")
            start = num
            end = num

    if start == end:
        ranges.append(f"{start}")
    else:
        ranges.append(f"{start}-{end}")

    return ", ".join(ranges)

async def sort_player_layout(request: Request, logger=Depends(get_logger), player_db=Depends(get_player_db), ini_dict=Depends(get_ini_dict)):
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
    all_players.sort(key=lambda p: p.channel_id)
    
    logger.info(f"POST Router | sort_video_player | Change layout: {layout} -> {num_players}")

    active_players = all_players[:num_players]
    inactive_players = all_players[num_players:]
    
    active_channel_ids = [player.channel_id for player in active_players]
    inactive_channel_ids = [player.channel_id for player in inactive_players]
    
    active_ranges = format_ranges(active_channel_ids)
    inactive_ranges = format_ranges(inactive_channel_ids)

    logger.info(f"POST Router | sort_player_layout | Active Players: {active_ranges}")
    logger.info(f"POST Router | sort_player_layout | Inactive Players: {inactive_ranges}")

    return JSONResponse(content={"detail": "Player layout updated successfully"})


async def get_video_info(player_idx: int, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    player = player_db.get_device_by_idx(player_idx)
    if not player or not player.onvif_result_address:
        return {"error": True, "message": "No video data available"}
    
    try:
        fps, codec, width, height, bit_rate = ffprobe(player.onvif_result_address, logger)
        return {
            "idx": player.idx,
            "fps": fps,
            "codec": codec,
            "width": width,
            "height": height,
            "bit_rate": bit_rate,
            "status": "good"
        }
    except RuntimeError as e:
        return {"error": True, "message": str(e)}