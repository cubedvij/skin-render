import base64
import typing
import aiohttp
import json

from PIL import Image
from io import BytesIO
from typing import Optional

from .skin import Skin

if typing.TYPE_CHECKING:
    from .player import Player
from config import AUTH_URL

__all__ = [
    "uuid_to_dashed",
    "uuid_to_undashed",
    "name_to_uuid",
    "uuid_to_name",
    "fetch_skin",
]


def uuid_to_dashed(uuid: str) -> str:
    return f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"


def uuid_to_undashed(uuid: str) -> str:
    return uuid.replace("-", "")


async def name_to_uuid(name: str, client: aiohttp.ClientSession = None) -> Optional[str]:
    if client is None:
        async with aiohttp.ClientSession() as client:
            async with client.get(f"{AUTH_URL}/users/profiles/minecraft/{name}") as response:
                if response.status == 200:
                    return (await response.json())["id"]
    else:
        async with client.get(f"{AUTH_URL}/users/profiles/minecraft/{name}") as response:
            if response.status == 200:
                return (await response.json())["id"]
    return None


async def uuid_to_name(uuid: str, client: aiohttp.ClientSession = None) -> Optional[str]:
    if client is None:
        async with aiohttp.ClientSession() as client:
            async with client.get(f"{AUTH_URL}/session/minecraft/profile/{uuid}") as response:
                if response.status == 200:
                    return (await response.json())["name"]
    else:
        async with client.get(f"{AUTH_URL}/session/minecraft/profile/{uuid}") as response:
            if response.status == 200:
                return (await response.json())["name"]

    if response.status == 200:
        return response.json()["name"]
    return None


async def fetch_skin(
        player: "Player" = None,
        name: str = None,
        uuid: str = None,
        client: aiohttp.ClientSession = None
) -> Optional[Skin]:
    if player is None and name is None and uuid is None:
        raise ValueError("At least one parameter must be passed")

    if client is None:
        async with aiohttp.ClientSession() as client:
            return await _fetch_skin_internal(player, name, uuid, client)
    else:
        return await _fetch_skin_internal(player, name, uuid, client)


async def _fetch_skin_internal(player, name, uuid, client: aiohttp.ClientSession):
    if player and player.uuid is not None:
        uuid = player.uuid

    if uuid is None and name is not None:
        uuid = await name_to_uuid(name, client)

    if uuid is not None:
        async with client.get(f"{AUTH_URL}/session/minecraft/profile/{uuid}") as response:
            if response.status == 200:
                cape = None
                skin = None
                resp_dict = await response.json()
                for p in resp_dict["properties"]:
                    if p["name"] == "textures":
                        textures = json.loads(base64.b64decode(p["value"]))["textures"]
                        skin_url = textures["SKIN"]["url"]
                        cape_url = textures["CAPE"]["url"] if "CAPE" in textures.keys() else None

                    if skin_url:
                        resp_skin = await client.get(skin_url)
                        if resp_skin.status == 200:
                            skin = Image.open(BytesIO(resp_skin.content))

                    if cape_url:
                        resp_cape = await client.get(cape_url)
                        if resp_cape.status == 200:
                            cape = Image.open(BytesIO(resp_cape.content))
                    break

    if skin is None:
        raise ValueError

    return Skin(
        raw_skin=skin,
        raw_cape=cape,
        raw_skin_url=skin_url,
        raw_cape_url=cape_url,
        name=resp_dict["name"]
    )
