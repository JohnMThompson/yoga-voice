# test_edge_list.py
# at the very top of test_edge_list.py and make_yoga_audio_edge.py
import os
for k in ("Ocp-Apim-Subscription-Key", "AZURE_TTS_KEY", "AZ_SPEECH_KEY"):
    os.environ.pop(k, None)
import asyncio, edge_tts

async def main():
    voices = await edge_tts.list_voices()
    print(len(voices), "voices available. Sample:", voices[0]["ShortName"])
asyncio.run(main())
