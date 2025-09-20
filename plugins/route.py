# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from info import *
from TechVJ.bot import multi_clients, work_loads, TechVJBot
from TechVJ.server.exceptions import FileNotFound, InvalidHash
from TechVJ import StartTime, __version__
from TechVJ.util.custom_dl import ByteStreamer
from TechVJ.util.time_format import get_readable_time
from TechVJ.util.render_template import render_page

logging.basicConfig(level=logging.DEBUG)
routes = web.RouteTableDef()

class_cache = {}

# Root route
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    logging.debug(f"Root route accessed from {request.remote}")
    return web.json_response("BenFilterBot")

# Watch route for HTML page
@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def watch_route_handler(request: web.Request):
    path = request.match_info["path"]
    logging.debug(f"Watch request for path: {path} from {request.remote}")
    try:
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            file_id = int(match.group(2))
        else:
            file_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return web.Response(text=await render_page(file_id, secure_hash), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FileNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        logging.warning("Temporary connection error")
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))

# General streaming route
@routes.get(r"/{path:\S+}", allow_head=True)
async def general_stream_handler(request: web.Request):
    path = request.match_info["path"]
    logging.debug(f"General stream request for path: {path} from {request.remote}")
    try:
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            file_id = int(match.group(2))
        else:
            file_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, file_id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FileNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        logging.warning("Temporary connection error")
    except Exception as e:
        logging.critical(e, exc_info=True)
        raise web.HTTPInternalServerError(text=str(e))

# Media streamer function
async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", None)
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    logging.debug(f"Using client {index} for request from {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
        logging.debug(f"Created new ByteStreamer object for client {index}")

    file_obj = await tg_connect.get_file_properties(id)
    
    if file_obj.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for file {id}")
        raise InvalidHash

    file_size = file_obj.file_size

    from_bytes, until_bytes = 0, file_size - 1
    if range_header and "bytes=" in range_header:
        try:
            parts = range_header.replace("bytes=", "").split("-")
            from_bytes = int(parts[0])
            until_bytes = int(parts[1]) if parts[1] else file_size - 1
        except Exception:
            logging.warning(f"Invalid Range header: {range_header}")

    chunk_size = 1024 * 1024
    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1
    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)

    body = tg_connect.yield_file(file_obj, index, offset, first_part_cut, last_part_cut, part_count, chunk_size)

    mime_type = file_obj.mime_type
    file_name = file_obj.file_name

    if not mime_type:
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = "application/octet-stream"

    if not file_name:
        file_name = f"{secrets.token_hex(2)}.unknown"

    disposition = "attachment"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
