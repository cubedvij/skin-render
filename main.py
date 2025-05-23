import os
from aiohttp import web
from minepi.player import Player
from config import CACHE_PATH

app = web.Application()
routes = web.RouteTableDef()

os.makedirs(CACHE_PATH, exist_ok=True)


async def get_image_response(
    uuid, cache_name, render_func, render_args=None, thumbnail=None
):
    player = Player(uuid=uuid)
    await player.initialize()
    skin = player.skin
    skin_hash = skin.skin_hash
    cape_hash = skin.cape_hash

    filename = cache_name.format(skin_hash=skin_hash, cape_hash=cape_hash)
    file_path = os.path.join(CACHE_PATH, filename)

    if os.path.isfile(file_path):
        return web.FileResponse(file_path, headers={"Content-Type": "image/png"})

    render_args = render_args or {}
    image = await getattr(skin, render_func)(**render_args)
    if image is None:
        return web.Response(status=404, text="Skin not found")

    if thumbnail:
        image.thumbnail(thumbnail)
    image.save(file_path)
    return web.FileResponse(file_path, headers={"Content-Type": "image/png"})


def uuid_required(handler):
    async def wrapper(request):
        uuid = request.match_info.get("uuid")
        if not uuid:
            return web.Response(status=400, text="UUID is required")
        return await handler(request, uuid)

    return wrapper


@routes.get("/avatars/{uuid}")
@uuid_required
async def get_avatar(request, uuid):
    return await get_image_response(
        uuid,
        cache_name="{skin_hash}-avatar.png",
        render_func="render_head",
        render_args={"vr": 0, "hr": 0},
    )


@routes.get("/head/{uuid}")
@uuid_required
async def get_head(request, uuid):
    return await get_image_response(
        uuid,
        cache_name="{skin_hash}-head.png",
        render_func="render_head",
        render_args={"vr": -35, "hr": 35},
    )


@routes.get("/player/{uuid}")
@uuid_required
async def get_player(request, uuid):
    return await get_image_response(
        uuid,
        cache_name="{skin_hash}-{cape_hash}-player.png",
        render_func="render_skin",
        render_args={
            "vr": -20,
            "hr": 30,
            "vrll": 30,
            "vrrl": -30,
            "vrla": -30,
            "vrra": 30,
            "aa": True,
        },
        thumbnail=(216, 392),
    )


@routes.get("/player-back/{uuid}")
@uuid_required
async def get_player_back(request, uuid):
    return await get_image_response(
        uuid,
        cache_name="{skin_hash}-{cape_hash}-player-back.png",
        render_func="render_skin",
        render_args={
            "vr": -20,
            "hr": 150,
            "vrll": -30,
            "vrrl": 30,
            "vrla": 30,
            "vrra": -30,
            "aa": True,
        },
        thumbnail=(216, 392),
    )


app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=9110)
