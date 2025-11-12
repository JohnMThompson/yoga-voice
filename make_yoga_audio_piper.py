import os, subprocess, tempfile
from pydub import AudioSegment

VOICE_MODEL = os.path.expanduser("~/piper-voices/en_US-lessac-high.onnx")
VOICE_JSON  = os.path.expanduser("~/piper-voices/en_US-lessac-high.onnx.json")

OUTPUT_WAV  = "yoga_flow_audio_full_piper.wav"
OUTPUT_MP3  = "yoga_flow_audio_full_piper.mp3"  # requires ffmpeg

# Segments: (text, hold_ms) — S1 pacing
segments = [
    ("Welcome John. We’ll begin with a breath reset. "
     "Take a comfortable seat or stand tall. Close your mouth gently. "
     "Breathe in through your nose for four, and out through your nose for six. "
     "Let your shoulders soften. Let your jaw loosen. We’ll begin.", 15000),

    ("Come to hands and knees for Cat–Cow. Wrists under shoulders, knees under hips. "
     "Inhale: drop your belly and open your chest slightly upward. "
     "Exhale: round your back and press the floor away. "
     "Match breath to movement. Inhale open. Exhale round. Smooth and steady.", 60000),

    ("Shift into Child’s Pose. Hips back toward your heels. "
     "Arms forward or resting by your sides. "
     "Breathe slowly. Let your shoulders drop and your ribs widen with each inhale.", 50000),

    ("Transition to Downward Dog. Tuck your toes and lift your hips up and back. "
     "Bend your knees as much as you like. "
     "Press the ground away and relax your neck. Let your head hang heavy. Slow breaths.", 60000),

    ("Step your right foot forward into Low Lunge. Back knee down. "
     "Lift your chest tall and let your right hip soften toward the floor. "
     "No forcing—just steady breathing.", 60000),

    ("Switch to the left side. Step your left foot forward, back knee down. "
     "Chest tall, shoulders easy. "
     "Breathe into the belly and let the hip melt with each exhale.", 60000),

    ("Half–kneeling hip flexor stretch on the right. "
     "Tuck your pelvis slightly—as if zipping up tight pants. "
     "Feel the stretch in the front of your right hip, not your low back. Small move, big effect.", 45000),

    ("Switch sides in the half–kneeling hip flexor stretch. "
     "Keep the gentle pelvic tuck. Relax your shoulders and breathe slowly.", 45000),

    ("Stand tall and fold forward into a Forward Fold. Knees soft. "
     "Let your arms and head hang like a ragdoll. Release your neck. "
     "Gentle sway if it feels good. Each exhale—soften a little deeper.", 75000),

    ("Tree Pose on the right. Shift weight into your right foot. "
     "Place your left foot at your calf or ankle—avoid the knee. "
     "Find a soft gaze. Wobbling is normal; step back in if you fall out.", 35000),

    ("Switch to Tree Pose on the left. Same calm breathing. "
     "Keep posture tall and jaw relaxed.", 35000),

    ("Lie on your back for Figure–4. Cross right ankle over left knee. "
     "Pull the left leg toward you or keep it light. "
     "Relax the jaw and hips with slow breathing.", 75000),

    ("Switch to the left side in Figure–4. Let gravity do the work. "
     "Breathe slowly.", 75000),

    ("Savasana. Settle on your back or with knees bent. "
     "Arms open, palms relaxed. Inhale for four, exhale for six. "
     "Let the body be heavy. Let today be enough.", 150000),

    ("When you are ready, deepen your breath, wiggle fingers and toes, "
     "roll gently to one side, and return to seated or standing. "
     "Your practice is complete.", 0),
]

def piper_tts(text, out_path, length_scale=1.05, noise_scale=0.5):
    """
    Works with both old (-m/-c) and new (--model) Piper CLIs.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Check which syntax this Piper supports
    help_text = subprocess.run(
        ["piper", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    ).stdout

    if "--model" in help_text:
        cmd = [
            "piper",
            "--model", VOICE_MODEL,
            "--output_file", out_path,
            "--length_scale", str(length_scale),
            "--noise_scale", str(noise_scale),
        ]
    else:
        cmd = [
            "piper",
            "-m", VOICE_MODEL,
            "-c", VOICE_JSON,
            "-f", out_path,
            "-s", str(length_scale),
            "-n", str(noise_scale),
        ]

    proc = subprocess.run(
        cmd, input=text.encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if proc.returncode != 0 or not os.path.exists(out_path):
        raise RuntimeError(f"Piper failed:\n{proc.stderr.decode()}")



def main():
    with tempfile.TemporaryDirectory() as td:
        combined = AudioSegment.silent(duration=0)
        for i, (text, hold_ms) in enumerate(segments, start=1):
            part = os.path.join(td, f"seg_{i:02d}.wav")
            print(f"[PIPER] Segment {i:02d}...")
            piper_tts(text, part, length_scale=1.07, noise_scale=0.5)  # slight slow-down, clean
            spoken = AudioSegment.from_file(part)
            combined += spoken
            if hold_ms > 0:
                combined += AudioSegment.silent(duration=hold_ms)

        print(f"[OUT] {OUTPUT_WAV}")
        combined.export(OUTPUT_WAV, format="wav")

        print(f"[OUT] {OUTPUT_MP3}")
        combined.export(OUTPUT_MP3, format="mp3", bitrate="192k")
        print("[OK] All done.")

if __name__ == "__main__":
    main()
