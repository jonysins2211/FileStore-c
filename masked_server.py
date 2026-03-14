from aiohttp import web
from database.database import db

routes = web.RouteTableDef()

@routes.get("/{hash_id}")
async def redirect_link(request):

    hash_id = request.match_info["hash_id"]

    data = await db.get_masked_link(hash_id)

    if not data:
        return web.Response(text="Invalid link")

    raise web.HTTPFound(data["target"])


app = web.Application()
app.add_routes(routes)


def run_server():
    web.run_app(app, host="0.0.0.0", port=8000)
