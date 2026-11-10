"""Build an offline-friendly, GitHub-Pages-ready demo from verified output files."""
from pathlib import Path
import csv
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MEDIA = DOCS / "media"
MEDIA.mkdir(parents=True, exist_ok=True)

cases = []
for case in json.loads((ROOT / "examples/manifest.json").read_text(encoding="utf-8")):
    label = case["label"]
    ident = label["video_id"]
    src_video = ROOT / "examples/videos" / label["filename"]
    src_result = ROOT / "examples/results" / ident
    paths = {
        "video": f"media/{ident}.mp4",
        "wav": f"media/{ident}.wav",
        "preview": f"media/{ident}.jpg",
        "subtitles": f"media/{ident}.srt",
        "transcript": f"media/{ident}.txt",
        "provenance": f"media/{ident}.json",
    }
    for src, key in [(src_video, "video"), (src_result / "description.wav", "wav"),
                     (src_result / "preview.jpg", "preview"),
                     (src_result / "captions.srt", "subtitles"),
                     (src_result / "description.txt", "transcript"),
                     (src_result / "result.json", "provenance")]:
        shutil.copy2(src, DOCS / paths[key])
    actual = json.loads((src_result / "result.json").read_text(encoding="utf-8"))
    cases.append({"id": ident, "shape": label["shape"], "color": label["color"],
                  "direction": label["direction"], "narration": actual["narration"], **paths})

metrics = json.loads((ROOT / "benchmarks/metrics.json").read_text(encoding="utf-8"))
with (ROOT / "benchmarks/predictions.csv").open(encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))
dirs = ["left", "right", "up", "down", "still"]
by_direction = [{"name": d, "count": sum(r["truth_direction"] == d for r in rows),
                 "correct": sum(r["direction_correct"] == "1" for r in rows if r["truth_direction"] == d)}
                for d in dirs]

page = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Video2Audio: reproducible computer vision to generated text and offline spoken WAV narration; examine four actual demos and an honest 120-video synthetic benchmark.">
  <title>Video2Audio | From frames to voice</title>
  <style>
    :root{--bg:#07101f;--surface:#0c1930;--surface2:#101f37;--stroke:#223752;--text:#edf4ff;--muted:#97aac8;--cyan:#55ead5;--blue:#70a1ff;--purple:#b09dfb;--gold:#f2ce81;--radius:18px}
    *{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 86% -12%,#1b3751 0,transparent 32%),radial-gradient(circle at -8% 45%,#122c43 0,transparent 26%),var(--bg);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.6}
    a{color:inherit;text-decoration:none}a:focus-visible,button:focus-visible{outline:3px solid var(--cyan);outline-offset:3px}button{font:inherit}img,video{max-width:100%}
    .wrap{max-width:1160px;padding:0 28px;margin:auto}.nav{height:85px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #1d3148}.brand{display:flex;align-items:center;gap:12px;font-size:18px;font-weight:850;letter-spacing:-.5px}.mark{width:35px;height:35px;display:grid;place-items:center;border-radius:11px;color:#051626;background:linear-gradient(130deg,#69f4db,#7daafe);font-weight:950}.navlinks{display:flex;gap:28px;font-size:13px;font-weight:600;color:#b0c3de}.navlinks a:hover{color:var(--cyan)}
    .hero{padding:80px 0 44px}.eyebrow{display:inline-flex;align-items:center;gap:9px;color:var(--cyan);text-transform:uppercase;font-size:11px;font-weight:800;letter-spacing:2px}.eyebrow:before{content:'';width:8px;height:8px;border-radius:50%;background:var(--cyan);box-shadow:0 0 12px #55ead588}.hero h1{font-size:clamp(42px,6.4vw,76px);line-height:1.08;letter-spacing:-4px;margin:20px 0 20px;max-width:875px}.gradient{background:linear-gradient(96deg,#77aaff 0%,#73eee0 55%,#b4a1ff 100%);-webkit-background-clip:text;background-clip:text;color:transparent}.hero p{font-size:17px;color:#a6bad4;max-width:710px;line-height:1.85;margin:0}.heroActions{display:flex;gap:13px;flex-wrap:wrap;margin:27px 0}.btn{display:inline-flex;align-items:center;justify-content:center;padding:12px 19px;border-radius:10px;background:var(--cyan);border:1px solid var(--cyan);color:#051725;font-weight:800;font-size:13px;cursor:pointer}.btn:hover{filter:brightness(1.07)}.btn.secondary{background:transparent;border-color:#45607e;color:#dce9ff}
    .truth{display:flex;gap:10px;align-items:flex-start;font-size:12px;color:#9fb4d0;padding:15px 18px;margin:16px 0 0;background:#102038;border:1px solid #2b405d;border-radius:11px;max-width:850px}.truth strong{color:#e1ecfc}
    .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:25px 0 78px}.stat{padding:22px 22px 18px;background:linear-gradient(160deg,#0f2138,#0b1629);border:1px solid var(--stroke);border-radius:15px}.stat .big{font-size:33px;letter-spacing:-1.5px;font-weight:850;line-height:1}.stat .detail{color:var(--muted);font-size:12px;margin-top:12px}.stat .source{font-size:10px;color:#7295bb;margin-top:6px}
    .section{padding:20px 0 72px}.sectionHeader{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:24px}.sectionHeader h2{font-size:32px;letter-spacing:-1.2px;margin:8px 0 0;line-height:1.2}.sectionHeader p{font-size:13px;color:var(--muted);max-width:390px}.kicker{color:var(--cyan);font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase}
    .pipeline{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.step{border:1px solid var(--stroke);background:#0d1b30;border-radius:16px;padding:22px 20px;position:relative}.stepNo{color:#55ead5;font-weight:900;font-size:12px;letter-spacing:1px}.step h3{font-size:15px;margin:15px 0 5px}.step p{color:#91a8c5;font-size:12px;line-height:1.7;margin:0}.step svg{height:31px;width:31px;margin-top:15px;stroke:#8dace5;stroke-width:1.6;fill:none}
    .playground{display:grid;grid-template-columns:1.45fr 1fr;gap:18px}.panel{border:1px solid var(--stroke);background:linear-gradient(160deg,#102039,#0c192d);border-radius:var(--radius);overflow:hidden}.panelHeader{display:flex;justify-content:space-between;align-items:center;padding:17px 20px;border-bottom:1px solid var(--stroke)}.panelTitle{font-size:13px;font-weight:750}.chip{font-size:10px;color:#82e8da;background:#13393e;padding:5px 8px;border:1px solid #205859;border-radius:6px;font-weight:750}.videoZone{background:#050e1e;min-height:320px;display:flex;align-items:center;justify-content:center;padding:23px}.videoZone video{width:100%;aspect-ratio:16/10;max-height:350px;object-fit:contain;background:#070f1b;border:1px solid #263e56;border-radius:10px}.gallery{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;padding:15px 18px}.thumb{padding:5px;background:#0a1527;border:1px solid #27415d;border-radius:10px;text-align:left;cursor:pointer;color:#afc4df}.thumb:hover,.thumb.active{border-color:var(--cyan);box-shadow:0 0 0 1px #55ead538}.thumb img{width:100%;aspect-ratio:16/10;object-fit:cover;border-radius:6px;display:block}.thumb span{display:block;padding:4px;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .descPanel{padding:21px}.meta{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:17px}.pill{color:#aac4de;border:1px solid #2a4963;border-radius:6px;background:#102940;padding:5px 9px;font-size:10px;text-transform:uppercase;font-weight:700}.descPanel h3{margin:0 0 10px;font-size:14px;color:#b0c9e5}.quote{font-size:19px;line-height:1.6;letter-spacing:-.2px;font-weight:550;min-height:115px;margin:0 0 28px}.audioTitle{font-size:11px;color:var(--cyan);font-weight:850;letter-spacing:1px;margin:16px 0 10px}.audioControl{width:100%;height:45px}.downloads{display:flex;gap:8px;flex-wrap:wrap;margin-top:17px}.dl{border:1px solid #385471;background:#11263e;padding:8px 11px;border-radius:8px;font-size:11px;color:#c4d7ee}.dl:hover{border-color:var(--cyan)}.smallNote{font-size:11px;color:#92a9c7;margin-top:17px;line-height:1.7}
    .benchmark{display:grid;grid-template-columns:.82fr 1.18fr;gap:22px}.infoPanel{padding:25px}.infoPanel h3{font-size:18px;margin:0 0 7px}.infoPanel p{font-size:13px;color:#a7bcd6;line-height:1.7;margin:0}.dataTags{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}.dataTags span{font-size:10px;color:#aec7e3;padding:5px 9px;border-radius:6px;border:1px solid #2e4968}.barPanel{padding:20px 25px}.barTitle{display:flex;justify-content:space-between;font-size:12px;color:#c3d3e8;margin-bottom:15px}.metricRow{display:grid;grid-template-columns:52px 1fr 50px;gap:12px;align-items:center;margin:12px 0;font-size:11px;color:#b4c6df}.track{height:10px;border-radius:12px;background:#213a53;overflow:hidden}.fill{height:100%;border-radius:12px;background:linear-gradient(90deg,#568fff,#55ead5)}.footnote{color:#809bbb;font-size:10px;margin-top:15px}
    .last{padding:26px 0 54px;border-top:1px solid #243952;color:#8fa6c6;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:12px}.last strong{color:#dce8fb}
    @media(max-width:920px){.stats,.pipeline{grid-template-columns:repeat(2,1fr)}.playground,.benchmark{grid-template-columns:1fr}.hero h1{letter-spacing:-2px}.hero{padding-top:54px}.navlinks{gap:12px}}
    @media(max-width:540px){.wrap{padding:0 17px}.nav{height:70px}.navlinks{font-size:11px;gap:10px}.stats{gap:9px;margin-bottom:50px}.stat{padding:16px}.stat .big{font-size:24px}.pipeline{grid-template-columns:1fr 1fr;gap:9px}.step{padding:15px}.hero h1{letter-spacing:-1.4px}.sectionHeader{display:block}.gallery{grid-template-columns:repeat(2,1fr)}.quote{font-size:16px}.videoZone{min-height:225px}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="nav"><a href="#home" class="brand"><span class="mark">V</span><span>video2audio<span style="color:var(--cyan)">.</span></span></a>
      <nav class="navlinks" aria-label="Site navigation"><a href="#pipeline">Pipeline</a><a href="#demo">Live examples</a><a href="#evaluation">Evaluation</a></nav>
    </header>
    <main id="home">
      <section class="hero">
        <div class="eyebrow">Computer vision · NLP · Offline speech</div>
        <h1>From moving pixels<br>to <span class="gradient">spoken meaning.</span></h1>
        <p>A Python engineering project that turns visual observations into grounded language and synthesized audio. Explore four real, precomputed video → speech examples and inspect results from a reproducible 120-clip synthetic benchmark.</p>
        <div class="heroActions"><a class="btn" href="#demo">Explore video demos ↗</a><a class="btn secondary" href="#pipeline">See the system architecture</a></div>
        <div class="truth"><span aria-hidden="true">ⓘ</span><span><strong>Transparent scope:</strong> Examples and reported scores use generated geometric shapes and deterministic OpenCV detection. Optional pretrained BLIP captioning is implemented for natural footage but <strong>not evaluated</strong> by this benchmark.</span></div>
      </section>
      <section class="stats" aria-label="Published synthetic benchmark metrics">
        <div class="stat"><div class="big">__NUM_CASES__</div><div class="detail">Synthetic clips processed</div><div class="source">Fully reproducible, generated in Python</div></div>
        <div class="stat"><div class="big" style="color:var(--cyan)">__AUDIO_CASES__</div><div class="detail">WAV narration files verified</div><div class="source">Checked before temporary file cleanup</div></div>
        <div class="stat"><div class="big">__SHAPE_ACC__%</div><div class="detail">Synthetic shape accuracy</div><div class="source">Shape classification, not semantic AI</div></div>
        <div class="stat"><div class="big">__DIR_ACC__%</div><div class="detail">Synthetic direction accuracy</div><div class="source">Largest-object centroid heuristic</div></div>
      </section>
      <section class="section" id="pipeline">
        <div class="sectionHeader"><div><div class="kicker">01 / Architecture</div><h2>Four stages. One complete output.</h2></div><p>Every stage is implemented as a separate Python module, independently testable and reproducible.</p></div>
        <div class="pipeline">
          <div class="step"><span class="stepNo">01 / INPUT</span><div><svg viewBox="0 0 32 32"><rect x="3" y="5" width="26" height="22" rx="3"/><path d="m13 11 9 5-9 5z"/></svg></div><h3>Decode & sample</h3><p>OpenCV extracts five time-spaced frames from each short MP4 video.</p></div>
          <div class="step"><span class="stepNo">02 / PERCEPTION</span><div><svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="11"/><path d="M16 5v22M5 16h22"/></svg></div><h3>Analyze frames</h3><p>Colored shape contours, or optional pretrained BLIP per-frame captions.</p></div>
          <div class="step"><span class="stepNo">03 / LANGUAGE</span><div><svg viewBox="0 0 32 32"><path d="M6 6h20v16H13l-7 5V6z"/><path d="M10 12h12M10 17h8"/></svg></div><h3>Compose narration</h3><p>Convert perceived objects and movement into an understandable text summary.</p></div>
          <div class="step"><span class="stepNo">04 / SPEECH</span><div><svg viewBox="0 0 32 32"><path d="M5 20h5l5 5V7l-5 5H5zM21 12c3 2 3 6 0 8M25 8c6 4 6 12 0 16"/></svg></div><h3>Export speech</h3><p>Offline TTS produces playable WAV audio, SRT subtitles, JSON and preview.</p></div>
        </div>
      </section>
      <section class="section" id="demo">
        <div class="sectionHeader"><div><div class="kicker">02 / Actual generated artifacts</div><h2>Watch it. Read it. Hear it.</h2></div><p>Choose a sample. Every MP4, prediction, WAV file and JSON report is a generated project artifact — not a placeholder.</p></div>
        <div class="playground">
          <div class="panel">
            <div class="panelHeader"><span class="panelTitle">INPUT / SYNTHETIC CLIP</span><span class="chip">VERIFIED MP4</span></div>
            <div class="videoZone"><video id="selectedVideo" controls playsinline muted preload="metadata" aria-label="Synthetic example video"></video></div>
            <div class="gallery" id="gallery" aria-label="Choose a demo clip"></div>
          </div>
          <div class="panel">
            <div class="panelHeader"><span class="panelTitle">OUTPUT / AUDIO DESCRIPTION</span><span class="chip">GENERATED WAV</span></div>
            <div class="descPanel"><div class="meta" id="caseMeta"></div><h3>Generated description</h3><p class="quote" id="narration" aria-live="polite"></p>
              <div class="audioTitle">▶ LISTEN TO THE GENERATED SPEECH</div>
              <audio id="selectedAudio" class="audioControl" controls preload="none" aria-label="Generated narrated audio"></audio>
              <div class="downloads"><a id="wavLink" class="dl" download>↓ WAV</a><a id="srtLink" class="dl" download>↓ SRT</a><a id="jsonLink" class="dl" download>↓ JSON</a><a id="txtLink" class="dl" download>↓ TXT</a></div>
              <div class="smallNote">These examples use the <strong>deterministic shapes baseline</strong>. Captions and audio were generated by the Python pipeline (not typed into this website). WAV narration is continuous, not time-synchronized to the video.</div>
            </div>
          </div>
        </div>
      </section>
      <section class="section" id="evaluation">
        <div class="sectionHeader"><div><div class="kicker">03 / Reproducibility</div><h2>Measurements, not marketing.</h2></div><p>Ground truth is produced separately and compared only after inference has been completed for each generated MP4.</p></div>
        <div class="benchmark">
          <div class="panel infoPanel"><h3>120-clip controlled benchmark</h3><p>Four shapes, four colors and five movement directions. All data are procedurally generated. 120 WAV files were synthesized and verified during this actual run. Raw prediction rows are committed in <code>benchmarks/predictions.csv</code>.</p>
            <div class="dataTags"><span>Seed: 2026</span><span>5 sampled frames</span><span>20 frames/video</span><span>2 sec/video</span><span>18 automated tests</span><span>Real-video BLIP score: N/A</span></div></div>
          <div class="panel barPanel"><div class="barTitle"><strong>Direction classification by true class</strong><span>correct / total</span></div><div id="bars"></div><div class="footnote">Direction may fail when apparent centroid displacement is too small; this is not a general action-recognition benchmark.</div></div>
        </div>
      </section>
    </main>
    <footer class="last"><span><strong>video2audio.</strong> · Reproducible Python engineering portfolio</span><span>OpenCV · Optional BLIP · Offline TTS · GitHub Actions</span></footer>
  </div>
  <script>
  const cases = __CASES_JSON__;
  const byDirection = __DIRECTION_JSON__;
  const gallery = document.getElementById('gallery');
  const $ = (name) => document.getElementById(name);
  let selected = 0;
  function selectCase(index) {
    selected = index;
    const c = cases[index];
    const video = $('selectedVideo'); const audio = $('selectedAudio');
    video.pause(); audio.pause();
    video.src = c.video; video.poster = c.preview; video.load();
    audio.src = c.wav; audio.load();
    $('narration').textContent = c.narration;
    $('caseMeta').replaceChildren();
    [c.color, c.shape, c.direction].forEach(val => { const t = document.createElement('span'); t.className = 'pill'; t.textContent = val; $('caseMeta').append(t); });
    $('wavLink').href = c.wav; $('srtLink').href = c.subtitles;
    $('jsonLink').href = c.provenance; $('txtLink').href = c.transcript;
    Array.from(gallery.children).forEach((el, i) => { el.classList.toggle('active', i === index); el.setAttribute('aria-pressed', i === index); });
  }
  cases.forEach((c, i) => {
    const button = document.createElement('button'); button.className = 'thumb'; button.type = 'button';
    button.setAttribute('aria-label', `Show video of ${c.color} ${c.shape} moving ${c.direction}`);
    const im = document.createElement('img'); im.src = c.preview; im.alt = `${c.color} ${c.shape}`; im.loading = 'lazy';
    const text = document.createElement('span'); text.textContent = `${String(i+1).padStart(2,'0')} · ${c.color} ${c.shape}`;
    button.append(im, text); button.addEventListener('click', () => selectCase(i)); gallery.append(button);
  });
  const maxCount = Math.max(...byDirection.map(d => d.count));
  byDirection.forEach(d => {
    const row = document.createElement('div'); row.className = 'metricRow';
    const l = document.createElement('span'); l.textContent = d.name;
    const track = document.createElement('div'); track.className = 'track';
    const fill = document.createElement('div'); fill.className = 'fill'; fill.style.width = `${100*d.correct/maxCount}%`;
    fill.title = `${d.correct} correct out of ${d.count}`; track.append(fill);
    const r = document.createElement('span'); r.textContent = `${d.correct}/${d.count}`;
    row.append(l, track, r); $('bars').append(row);
  });
  selectCase(0);
  </script>
</body></html>
'''
page = (page.replace("__CASES_JSON__", json.dumps(cases, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__DIRECTION_JSON__", json.dumps(by_direction, ensure_ascii=False))
            .replace("__NUM_CASES__", str(metrics["video_count"]))
            .replace("__AUDIO_CASES__", str(metrics["audio_files_verified"]))
            .replace("__SHAPE_ACC__", f'{metrics["shape_accuracy"]*100:.0f}')
            .replace("__DIR_ACC__", f'{metrics["direction_accuracy"]*100:.2f}'))
(DOCS / "index.html").write_text(page, encoding="utf-8")
print(f"Built docs/index.html from {len(cases)} real cases and {len(rows)} benchmark rows")
