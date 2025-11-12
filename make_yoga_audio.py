from pydub import AudioSegment
import pyttsx3, os, tempfile
import time

# ----------------------------
# Settings you can tweak
# ----------------------------
VOICE_RATE = 155
OUTPUT_WAV = "yoga_flow_audio_full.wav"
OUTPUT_MP3 = "yoga_flow_audio_full.mp3"   # requires ffmpeg
ADD_ROOM_TONE_DB = -38  # relative loudness of room tone (higher negative = quieter)
ROOM_TONE = AudioSegment.silent(duration=1000)  # 1-second neutral room tone


# Try to pick a "male" voice if available (Linux Mint often uses eSpeak voices)
def pick_voice(engine):
    try:
        voices = engine.getProperty("voices")
        # Prefer male English if listed
        for v in voices:
            name = (v.name or "").lower()
            lang = "".join(v.languages[0]).lower() if v.languages else ""
            if "male" in name and ("en" in lang or "english" in name):
                engine.setProperty("voice", v.id)
                return
        # Fallback: any English voice
        for v in voices:
            name = (v.name or "").lower()
            lang = "".join(v.languages[0]).lower() if v.languages else ""
            if "en" in lang or "english" in name:
                engine.setProperty("voice", v.id)
                return
    except Exception:
        pass  # use default

# Script segments + silence (milliseconds) for S1 pacing
segments = [
    ("Welcome John. We’ll begin with a breath reset. "
     "Take a comfortable seat or stand tall. Close your mouth gently. "
     "Breathe in through your nose for four, and out through your nose for six. "
     "Let your shoulders soften. Let your jaw loosen. We’ll begin.",
     15_000),

    ("Come to hands and knees for Cat–Cow. Wrists under shoulders, knees under hips. "
     "Inhale: drop your belly and open your chest slightly upward. "
     "Exhale: round your back and press the floor away. "
     "Match breath to movement. Inhale open. Exhale round. Smooth and steady.",
     60_000),

    ("Shift into Child’s Pose. Hips back toward your heels. "
     "Arms forward or resting by your sides. "
     "Breathe slowly. Let your shoulders drop and your ribs widen with each inhale.",
     50_000),

    ("Transition to Downward Dog. Tuck your toes and lift your hips up and back. "
     "Bend your knees as much as you like. "
     "Press the ground away and relax your neck. Let your head hang heavy. Slow breaths.",
     60_000),

    ("Step your right foot forward into Low Lunge. Back knee down. "
     "Lift your chest tall and let your right hip soften toward the floor. "
     "No forcing—just steady breathing.",
     60_000),

    ("Switch to the left side. Step your left foot forward, back knee down. "
     "Chest tall, shoulders easy. "
     "Breathe into the belly and let the hip melt with each exhale.",
     60_000),

    ("Half–kneeling hip flexor stretch on the right. "
     "Tuck your pelvis slightly—as if zipping up tight pants. "
     "Feel the stretch in the front of your right hip, not your low back. Small move, big effect.",
     45_000),

    ("Switch sides in the half–kneeling hip flexor stretch. "
     "Keep the gentle pelvic tuck. Relax your shoulders and breathe slowly.",
     45_000),

    ("Stand tall and fold forward into a Forward Fold. Knees soft. "
     "Let your arms and head hang like a ragdoll. Release your neck. "
     "Gentle sway if it feels good. Each exhale—soften a little deeper.",
     75_000),

    ("Tree Pose on the right. Shift weight into your right foot. "
     "Place your left foot at your calf or ankle—avoid the knee. "
     "Find a soft gaze. Wobbling is normal; step back in if you fall out.",
     35_000),

    ("Switch to Tree Pose on the left. Same calm breathing. "
     "Keep posture tall and jaw relaxed.",
     35_000),

    ("Lie on your back for Figure–4. Cross right ankle over left knee. "
     "Pull the left leg toward you or keep it light. "
     "Relax the jaw and hips with slow breathing.",
     75_000),

    ("Switch to the left side in Figure–4. Let gravity do the work. "
     "Breathe slowly.",
     75_000),

    ("Savasana. Settle on your back or with knees bent. "
     "Arms open, palms relaxed. Inhale for four, exhale for six. "
     "Let the body be heavy. Let today be enough.",
     150_000),

    ("When you are ready, deepen your breath, wiggle fingers and toes, "
     "roll gently to one side, and return to seated or standing. "
     "Your practice is complete.",
     0),
]

def synth_to_wav(text, outfile, rate=VOICE_RATE):
    engine = pyttsx3.init()
    pick_voice(engine)
    engine.setProperty("rate", rate)
    engine.save_to_file(text, outfile)
    engine.runAndWait()

    # wait until file is created
    for _ in range(20):  # wait up to ~10 seconds total
        if os.path.exists(outfile) and os.path.getsize(outfile) > 0:
            break
        time.sleep(0.5)
    else:
        raise RuntimeError(f"TTS output file not found or empty: {outfile}")

def main():
    with tempfile.TemporaryDirectory() as td:
        combined = AudioSegment.silent(duration=0)
        room_tone = ROOM_TONE - 0  # base tone (we’ll overlay to avoid absolute silence)

        for i, (text, silence_ms) in enumerate(segments, start=1):
            part_path = os.path.join(td, f"seg_{i:02d}.wav")
            print(f"[TTS] Rendering segment {i:02d}...")
            synth_to_wav(text, part_path)
            print(f"[OK] Segment {i:02d} created at {part_path}")

            spoken = AudioSegment.from_file(part_path)
            # Add a very light neutral room tone under speech to avoid dead-silent floor
            # (mix in quiet tone equal to speech duration)
            if ADD_ROOM_TONE_DB is not None:
                rt = AudioSegment.silent(duration=len(spoken)).overlay(room_tone - abs(ADD_ROOM_TONE_DB))
                spoken = spoken.overlay(rt)

            combined += spoken

            # Add silence hold for the pose if any
            if silence_ms > 0:
                # Use gentle room tone instead of absolute silence
                hold = AudioSegment.silent(duration=silence_ms).overlay(room_tone - abs(ADD_ROOM_TONE_DB))
                combined += hold

        print(f"[OUT] Writing {OUTPUT_WAV} ...")
        combined.export(OUTPUT_WAV, format="wav")
        print("[OK] WAV complete.")

        # Optional MP3
        try:
            print(f"[OUT] Writing {OUTPUT_MP3} ...")
            combined.export(OUTPUT_MP3, format="mp3", bitrate="192k")
            print("[OK] MP3 complete.")
        except Exception as e:
            print("[WARN] MP3 export failed (install ffmpeg). WAV is ready.")
            print(e)

if __name__ == "__main__":
    main()
