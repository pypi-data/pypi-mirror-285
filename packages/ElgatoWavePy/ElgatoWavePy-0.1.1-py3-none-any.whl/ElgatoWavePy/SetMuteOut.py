import asyncio
import websockets
import json



MIXERS = {
    "local": "com.elgato.mix.local",
    "stream": "com.elgato.mix.stream"
}


# Fonction asynchrone pour gérer la connexion WebSocket
async def async_set_mute_output(mixer, value, websocket_url="ws://127.0.0.1", port="1824"):
    url = f"{websocket_url}:{port}"
    async with websockets.connect(url) as ws:
        message = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "setOutputConfig",
                "params": {
                    "property": "Output Mute",
                    "mixerID": mixer,
                    "value": value,
                    "forceLink": False              
            }
        }
        await ws.send(json.dumps(message))
        # Optionnel : Attendre une réponse ou ajouter d'autres opérations

# Fonction synchrone pour l'interface utilisateur
def SetMuteOutput(value: bool, mixer_id=None, websocket_url="ws://127.0.0.1", port="1824"):
    # Créer et exécuter une boucle d'événements
    if mixer_id in MIXERS:
        mixer_id = MIXERS[mixer_id]

    if mixer_id is None:
        raise ValueError("Mixer Key Invalid")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(async_set_mute_output(mixer_id, value, websocket_url, port))
    finally:
        loop.close()

