# Skin Render API
This is a simple API for rendering Minecraft skins using aiohttp.

## Endpoints
- `GET /avatars/{uuid}`: Get the avatar image for a player.
- `GET /head/{uuid}`: Get the head image for a player.
- `GET /player/{uuid}`: Get the player image for a player.
- `GET /player-back/{uuid}`: Get the player back image for a player.

## Running the API
To run the API, execute the following command:
```bash
python main.py
```
The API will be available at `http://localhost:9110`.
## Example Usage
```bash
curl -X GET http://localhost:9110/avatars/{uuid}
```
