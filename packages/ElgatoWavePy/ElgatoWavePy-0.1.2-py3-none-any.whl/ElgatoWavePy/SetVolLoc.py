import asyncio
import websockets
import json

# Fonction asynchrone pour gérer la connexion WebSocket
async def async_set_volume_local(volume, websocket_url="ws://127.0.0.1", port="1824"):
    url = f"{websocket_url}:{port}"
    async with websockets.connect(url) as ws:
        message = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "setOutputConfig",
            "params": {
                "property": "Output Level",
                "mixerID": "com.elgato.mix.local",
                "value": volume,
                "forceLink": False              
            }
        }
        await ws.send(json.dumps(message))
        # Optionnel : Attendre une réponse ou ajouter d'autres opérations

# Fonction synchrone pour l'interface utilisateur
def SetVolumeLocal(volume: int, websocket_url="ws://127.0.0.1", port="1824"):
    # Créer et exécuter une boucle d'événements
    if 0 < volume < 100:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_set_volume_local(volume, websocket_url, port))
        finally:
            loop.close()
    else:
        raise ValueError("Volume need to be between 0 and 100")