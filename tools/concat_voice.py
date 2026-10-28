#!/usr/bin/env python3
"""Join per-line narration WAVs (from audio_meta.json) into one track with fixed gaps, and write the
line start times so scenes can be timed to the voice. Standard library only; deterministic.

    python3 tools/concat_voice.py <project dir> [--lead 0.8] [--gap 1.6] [--tail 3.0]

Writes <project>/assets/voice/narration.wav and <project>/timing.json:
{"lead": .., "gap": .., "lines": [{"id": "s1", "start": 0.8, "end": 7.26, "duration": 6.46}, ...], "total": ..}
"""
import json
import pathlib
import sys
import wave


def main(argv):
    proj = pathlib.Path(argv[1]).resolve()
    opts = {"--lead": 0.8, "--gap": 1.6, "--tail": 3.0}
    for i, a in enumerate(argv):
        if a in opts and i + 1 < len(argv):
            opts[a] = float(argv[i + 1])
    meta = json.loads((proj / "audio_meta.json").read_text())
    voices = meta["voices"]
    if isinstance(voices, dict):
        voices = [dict(v, id=k) for k, v in voices.items()]
    order = [l["id"] for l in json.loads((proj / "audio_request.json").read_text())["lines"]]
    by_id = {v.get("id") or v.get("line_id"): v for v in voices}
    params = None
    frames_out = []
    lines = []
    t = opts["--lead"]

    def silence(seconds):
        n = int(round(seconds * params.framerate))
        return b"\x00" * (n * params.sampwidth * params.nchannels)

    for lid in order:
        v = by_id[lid]
        with wave.open(str(proj / v["path"]), "rb") as w:
            p = w.getparams()
            if params is None:
                params = p
                frames_out.append(silence(opts["--lead"]))
            elif (p.framerate, p.sampwidth, p.nchannels) != (params.framerate, params.sampwidth, params.nchannels):
                sys.exit(f"{v['path']} has different wav params")
            data = w.readframes(w.getnframes())
            dur = w.getnframes() / p.framerate
        lines.append({"id": lid, "start": round(t, 3), "end": round(t + dur, 3), "duration": round(dur, 3)})
        frames_out.append(data)
        frames_out.append(silence(opts["--gap"]))
        t += dur + opts["--gap"]
    frames_out.append(silence(max(opts["--tail"] - opts["--gap"], 0)))
    total = t - opts["--gap"] + opts["--tail"]
    out = proj / "assets" / "voice" / "narration.wav"
    with wave.open(str(out), "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(frames_out))
    (proj / "timing.json").write_text(json.dumps({"lead": opts["--lead"], "gap": opts["--gap"], "tail": opts["--tail"], "lines": lines, "total": round(total, 3)}, indent=1))
    print(f"wrote {out} ({total:.2f}s, {params.framerate} Hz, {params.nchannels} ch) and timing.json with {len(lines)} lines")
    for l in lines:
        print(f"  {l['id']:4s} {l['start']:6.2f} -> {l['end']:6.2f}  ({l['duration']:.2f}s)")


if __name__ == "__main__":
    main(sys.argv)
