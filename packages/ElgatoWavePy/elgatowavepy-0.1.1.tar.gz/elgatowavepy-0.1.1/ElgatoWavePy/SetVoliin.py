# library.py

import asyncio
import websockets
import json

# Valeurs prédéfinies pour les inputs
INPUTS = {
    "System": "PCM_OUT_01_V_00_SD2",
    "Music": "PCM_OUT_01_V_02_SD3",
    "Browser": "PCM_OUT_01_V_04_SD4",
    "VoiceChat": "PCM_OUT_01_V_06_SD5",
    "SFX": "PCM_OUT_01_V_08_SD6",
    "Game": "PCM_OUT_01_V_10_SD7",
    "Aux1": "PCM_OUT_01_V_12_SD8",
    "Aux2": "PCM_OUT_01_V_14_SD9"
}

# Valeurs prédéfinies pour les mixers
MIXERS = {
    "local": "com.elgato.mix.local",
    "stream": "com.elgato.mix.stream"
}

# Fonction asynchrone pour gérer la connexion WebSocket
async def async_set_volume_input(volume, input_id, mixer_id, websocket_url="ws://127.0.0.1", port="1824"):
    url = f"{websocket_url}:{port}"
    async with websockets.connect(url) as ws:
        message = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "setInputConfig",
            "params": {
                "property": "Volume",
                "identifier": input_id,
                "mixerID": mixer_id,
                "forceLink": False,
                "value": volume
            }
        }
        await ws.send(json.dumps(message))
        # Optionnel : Attendre une réponse ou ajouter d'autres opérations

# Fonction synchrone pour l'interface utilisateur
def SetVolumeInput(volume: int, input_id=None, mixer_id=None, websocket_url="ws://127.0.0.1", port="1824"):
    # Utiliser des valeurs par défaut si input_id ou mixer_id sont None
    if input_id in INPUTS:
        input_id = INPUTS[input_id]
    if mixer_id in MIXERS:
        mixer_id = MIXERS[mixer_id]
    
    # Vérifier que les valeurs sont valides
    if input_id is None or mixer_id is None:
        raise ValueError("input Key or Mixer Key Invalid")
    
    if 0 < volume < 100:
        # Créer et exécuter une boucle d'événements
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_set_volume_input(volume, input_id, mixer_id, websocket_url, port))
        finally:
            loop.close()
    else:
        raise ValueError("Volume need to be between 0 and 100")