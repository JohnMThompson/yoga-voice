import asyncio, os, tempfile
import edge_tts
from pydub import AudioSegment

VOICE = "en-US-GuyNeural"  # other good ones: en-US-DavisNeural, en-US-EricNeural
RATE  = "-5%"              # slower pace; try 0% or -10%
OUTPUT_WAV = "yoga_flow_audio_full_edge.wav"
OUTPUT_MP3 = "yoga_flow_audio_full_edge.mp3"

segments = [
    ("Welcome John. We’ll begin with a breath reset. "
     "Take a comfortable seat or stand tall. Close your mouth gently. "
     "Breathe in through your nose for four, and out through your nose for six. "
     "Let your shoulders soften. Let your jaw loosen. We’ll begin.", 15_000),
    ("Come to hands and knees for Cat–Cow. Wrists under shoulders, knees under hips. "
     "Inhale: drop your belly and open your chest slightly upward. "
     "Exhale: round your back and press the floor away. "
     "Match breath to movement. Inhale open. Exhale round. Smooth and steady.", 60_000),
    ("Shift into Child’s Pose. Hips back toward your heels. "
     "Arms forward or resting by your sides. "
     "Breathe slowly. Let your shoulders drop and your ribs widen with each inhale.", 50_000),
    ("Transition to Downward Dog. Tuck your toes and lift your hips up and back. "
     "Bend your knees as much as you like. "
     "Press the ground away and relax your neck. Let your head hang heavy. Slow breaths.", 60_000),
    ("Step your right foot forward into Low Lunge. Back knee down. "
     "Lift your chest tall and let your right hip soften toward the floor. "
     "No forcing—just steady breathing.", 60_000),
    ("Switch to the left side. Step your left foot forward, back knee down. "
     "Chest tall, shoulders easy. "
     "Breathe into the belly and let the hip melt with each exhale.", 60_000),
    ("Half–kneeling hip flexor stretch on the right. "
     "Tuck your pelvis slightly—as if zipping up tight pants. "
     "Feel the stretch in the front of your right hip, not your low back. Small move, big effect.", 45_000),
    ("Switch sides in the half–kneeling hip flexor stretch. "
     "Keep the gentle pelvic tuck. Relax your shoulders and breathe slowly.", 45_000),
    ("Stand tall and fold forward into a Forward Fold. Knees soft. "
     "Let your arms and head hang like a ragdoll. Release your neck. "
     "Gentle sway if it feels good. Each exhale—soften a little deeper.", 75_000),
    ("Tree Pose on the right. Shift weight into your right foot. "
     "Place your left foot at your calf or ankle—avoid the knee. "
     "Find a soft gaze. Wobbling is normal; step back in if you fall out.", 35_000),
    ("Switch to Tree Pose on the left. Same calm breathing. "
     "Keep posture tall and jaw relaxed.", 35_000),
    ("Lie on your back for Figure–4. Cross right ankle over left knee. "
     "Pull the left leg toward you or keep it light. "
     "Relax the jaw and hips with slow breathing.", 75_000),
    ("Switch to the left side in Figure–4. Let gravity do the work. "
     "Breathe slowly.", 75_000),
    ("Savasana. Settle on your back or with knees bent. "
     "Arms open, palms relaxed. Inhale for four, exhale for six. "
     "Let the body be heavy. Let today be enough.", 150_000),
    ("When you are ready, deepen your breath, wiggle fingers and toes, "
     "roll gently to one side, and return to seated or standing. "
     "Your practice is complete.", 0),
]

async def tts_to_file(text, path):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(path)

async def main():
    with tempfile.TemporaryDirectory() as td:
        combo = AudioSegment.silent(duration=0)
        for i, (text, hold_ms) in enumerate(segments, start=1):
            part = os.path.join(td, f"seg_{i:02d}.mp3")
            print(f"[TTS] Segment {i:02d}...")
            await tts_to_file(text, part)
            spoken = AudioSegment.from_file(part)
            combo += spoken
            if hold_ms > 0:
                # neutral room tone via -60dB “silence”
                combo += AudioSegment.silent(duration=hold_ms)
        print(f"[OUT] {OUTPUT_WAV}")
        combo.export(OUTPUT_WAV, format="wav")
        print(f"[OUT] {OUTPUT_MP3}")
        combo.export(OUTPUT_MP3, format="mp3", bitrate="192k")
        print("[OK] All done.")

if __name__ == "__main__":
    asyncio.run(main())
