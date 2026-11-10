"""Run with: python app.py (pip install -e '.[ui]')."""
from pathlib import Path
import tempfile
import uuid
import gradio as gr
from video2audio.pipeline import process_video

OUT = Path(tempfile.gettempdir()) / "video2audio_gradio"
OUT.mkdir(parents=True, exist_ok=True)


def describe(video_path, backend, language, samples):
    if not video_path:
        raise gr.Error("Upload a video first.")
    try:
        output_dir = OUT / uuid.uuid4().hex
        result = process_video(video_path, output_dir, backend=backend, language=language,
                               samples=int(samples), audio=True)
    except Exception as exc:
        raise gr.Error(str(exc)) from exc
    return (result.narration, str(output_dir / "description.wav"),
            str(output_dir / "preview.jpg"), str(output_dir / "result.json"))


with gr.Blocks(title="Video2Audio | Accessible video descriptions") as app:
    gr.Markdown("# Video2Audio — Video → Visual Description → Narrated Audio")
    gr.Markdown("**Portfolio demo.** The *Shapes* backend only understands colored geometric figures. "
                "Choose *BLIP (pretrained AI)* for general videos after installing optional dependencies; "
                "its captions may be inaccurate and should be reviewed before accessibility use.")
    with gr.Row():
        with gr.Column():
            video = gr.Video(label="Input video (MP4 preferred)")
            backend = gr.Dropdown([("Shapes — deterministic demo", "shapes"),
                                   ("BLIP — pretrained AI, model download required", "blip")],
                                  value="shapes", label="Vision backend")
            language = gr.Dropdown(["en", "fr"], value="en", label="Narration language (BLIP: English only)")
            samples = gr.Slider(2, 10, value=5, step=1, label="Sampled frames")
            run = gr.Button("Generate description + audio", variant="primary")
        with gr.Column():
            description = gr.Textbox(label="Generated description", lines=5)
            wav = gr.Audio(label="Generated spoken WAV", type="filepath")
            preview = gr.Image(label="Visual detection preview")
            report = gr.File(label="Download provenance + frame-level JSON")
    run.click(describe, [video, backend, language, samples], [description, wav, preview, report])
    gr.Markdown("**Privacy:** uploads are processed on the machine running this app; the BLIP model "
                "is downloaded from Hugging Face on first use. No video is sent to a hosted inference API.")

if __name__ == "__main__":
    app.launch()
