from aiohttp import web
from database.database import db

routes = web.RouteTableDef()

@routes.get("/{hash_id}")
async def masked_redirect(request):

    hash_id = request.match_info["hash_id"]

    data = await db.get_masked_link(hash_id)

    if not data:
        return web.Response(text="Invalid link")

    raise web.HTTPFound(data["target"])
