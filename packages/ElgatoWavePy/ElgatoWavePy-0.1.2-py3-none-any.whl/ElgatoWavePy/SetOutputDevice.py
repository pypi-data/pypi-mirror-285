import asyncio
import websockets
import json

# Fonction asynchrone pour gérer la connexion WebSocket
async def async_set_output(identifier, name, websocket_url="ws://127.0.0.1", port="1824"):
    url = f"{websocket_url}:{port}"
    async with websockets.connect(url) as ws:
        message = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "setSelectedOutput",
            "params": {
                "identifier": identifier,
                "name": name           
            }
        }
        await ws.send(json.dumps(message))
        # Optionnel : Attendre une réponse ou ajouter d'autres opérations

# Fonction synchrone pour l'interface utilisateur
def SetOutput(identifier: str, name: str, websocket_url="ws://127.0.0.1", port="1824"):
    # Créer et exécuter une boucle d'événements
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_set_output(identifier, name, websocket_url, port))
    finally:
        loop.close()


