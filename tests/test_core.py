"""Core tests: schema contract, verdict policy, aggregates, text extraction, Jev cache with a stubbed API."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))

from lib import config, fetch, jev, schema, score  # noqa: E402


class SchemaTests(unittest.TestCase):
    def test_sources_require_known_format_and_access(self):
        schema.validate_sources([{"id": "s1", "url": "u", "title": "t", "date": "2025-12-23", "format": "newsletter", "access": "free"}])
        with self.assertRaises(schema.SchemaError):
            schema.validate_sources([{"id": "s1", "url": "u", "title": "t", "date": "2025-12-23", "format": "blog", "access": "free"}])
        with self.assertRaises(schema.SchemaError):
            schema.validate_sources([{"id": "s1", "url": "u", "title": "t", "date": "d", "format": "essay", "access": "free"},
                                     {"id": "s1", "url": "u", "title": "t", "date": "d", "format": "essay", "access": "free"}])

    def test_claims_reference_sources(self):
        sources = [{"id": "s1", "url": "u", "title": "t", "date": "d", "format": "essay", "access": "free"}]
        schema.validate_claims([{"id": "c1", "source_id": "s1", "quote": "q", "date": "d", "author": "a"}], sources)
        with self.assertRaises(schema.SchemaError):
            schema.validate_claims([{"id": "c1", "source_id": "s9", "quote": "q", "date": "d", "author": "a"}], sources)

    def test_rubrics_need_all_three_bars(self):
        claims = [{"id": "c1", "source_id": "s1", "quote": "q", "date": "d", "author": "a"}]
        good = [{"claim_id": "c1", "bars": {b: {"criterion": "x"} for b in config.BARS}}]
        schema.validate_rubrics(good, claims)
        bad = [{"claim_id": "c1", "bars": {"strict": {"criterion": "x"}, "standard": {"criterion": "y"}}}]
        with self.assertRaises(schema.SchemaError):
            schema.validate_rubrics(bad, claims)

    def test_evidence_tier_and_direction(self):
        claims = [{"id": "c1", "source_id": "s1", "quote": "q", "date": "d", "author": "a"}]
        row = {"id": "e1", "claim_id": "c1", "url": "u", "date": "2026-02-01", "source": "Reuters", "tier": 2, "quote": "q", "direction": "supports"}
        schema.validate_evidence([row], claims)
        with self.assertRaises(schema.SchemaError):
            schema.validate_evidence([{**row, "tier": 7}], claims)
        with self.assertRaises(schema.SchemaError):
            schema.validate_evidence([{**row, "direction": "maybe"}], claims)
        with self.assertRaises(schema.SchemaError):
            schema.validate_evidence([{**row, "bars": ["loose"]}], claims)

    def test_jsonl_round_trip_skips_comments_and_blanks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl"
            p.write_text('# comment\n{"a": 1}\n\n{"a": 2}\n')
            self.assertEqual([r["a"] for r in schema.read_jsonl(p)], [1, 2])
            schema.write_jsonl(p, [{"b": "é"}])
            self.assertEqual(schema.read_jsonl(p), [{"b": "é"}])


class VerdictTests(unittest.TestCase):
    T = config.THRESHOLDS

    def test_met_needs_probability_and_standing(self):
        self.assertEqual(score.verdict(0.9, 0.05, 1.6, self.T)[0], "met")
        self.assertEqual(score.verdict(0.9, 0.05, 0.4, self.T), ("unresolved", "claimed but the evidence lacks standing"))

    def test_not_met_on_contradiction(self):
        self.assertEqual(score.verdict(0.1, 0.9, 1.8, self.T)[0], "not_met")

    def test_conflict_and_silence_are_unresolved(self):
        self.assertEqual(score.verdict(0.8, 0.8, 1.8, self.T), ("unresolved", "evidence conflicts"))
        self.assertEqual(score.verdict(0.1, 0.1, 0.0, self.T), ("unresolved", "evidence is silent"))
        self.assertEqual(score.verdict(0.5, 0.4, 1.0, self.T), ("unresolved", "grader is uncertain"))

    def test_monotone_propagates_met_down_and_not_met_up(self):
        grades = [{"claim_id": "c1", "bar": "strict", "verdict": "met", "reason": "x"},
                  {"claim_id": "c1", "bar": "standard", "verdict": "unresolved", "reason": "x"},
                  {"claim_id": "c1", "bar": "lenient", "verdict": "unresolved", "reason": "x"},
                  {"claim_id": "c2", "bar": "strict", "verdict": "unresolved", "reason": "x"},
                  {"claim_id": "c2", "bar": "standard", "verdict": "not_met", "reason": "x"},
                  {"claim_id": "c2", "bar": "lenient", "verdict": "met", "reason": "x"},
                  {"claim_id": "c3", "bar": "strict", "verdict": "not_met", "reason": "x"},
                  {"claim_id": "c3", "bar": "standard", "verdict": "unresolved", "reason": "x"},
                  {"claim_id": "c3", "bar": "lenient", "verdict": "met", "reason": "x"}]
        changed = score.monotone(grades)
        v = {(g["claim_id"], g["bar"]): g["verdict"] for g in grades}
        self.assertEqual(changed, 3)
        self.assertEqual((v["c1", "standard"], v["c1", "lenient"]), ("met", "met"))
        self.assertEqual((v["c2", "strict"], v["c2", "lenient"]), ("not_met", "met"))  # lenient met stands; strict follows standard
        self.assertEqual((v["c3", "strict"], v["c3", "standard"], v["c3", "lenient"]), ("not_met", "unresolved", "met"))  # already consistent
        self.assertEqual(grades[1]["implied_from"], "strict")

    def test_aggregate_hit_rates_and_gap(self):
        claims = [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}]
        grades = []
        for cid, verdicts in {"c1": ("met", "met", "met"), "c2": ("not_met", "not_met", "met"), "c3": ("unresolved", "unresolved", "unresolved")}.items():
            for bar, v in zip(config.BARS, verdicts):
                grades.append({"claim_id": cid, "bar": bar, "verdict": v})
        agg = score.aggregate(grades, claims)
        self.assertEqual(agg["per_bar"]["strict"]["met"], 1)
        self.assertEqual(agg["per_bar"]["lenient"]["met"], 2)
        self.assertAlmostEqual(agg["generosity_gap"], round(2 / 3 - 1 / 3, 3))
        self.assertEqual(agg["ladder"], {"c1": "met:strict", "c2": "met:lenient", "c3": "unresolved"})
        self.assertEqual(agg["ladder_counts"]["met_lenient"], 1)


class TextTests(unittest.TestCase):
    def test_html_to_text_drops_scripts_and_keeps_blocks(self):
        html = "<html><head><title>T</title><script>x()</script></head><body><nav>menu</nav><p>One.</p><p>Two.</p></body></html>"
        text, title = fetch.html_to_text(html)
        self.assertEqual(title, "T")
        self.assertNotIn("x()", text)
        self.assertNotIn("menu", text)
        self.assertIn("One.\n\nTwo.", text)

    def test_vtt_to_text_collapses_rolling_duplicates(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nhello <c>world</c>\n\n00:00:02.000 --> 00:00:03.000\nhello world\n\n00:00:03.000 --> 00:00:04.000\nagain &amp; again\n"
        self.assertEqual(fetch.vtt_to_text(vtt), "hello world again & again")


class JevTests(unittest.TestCase):
    def test_hash_is_order_independent(self):
        a = jev.request_hash("m", {"x": 1, "y": 2}, {"q": {"type": "noul", "instructions": "i"}})
        b = jev.request_hash("m", {"y": 2, "x": 1}, {"q": {"instructions": "i", "type": "noul"}})
        self.assertEqual(a, b)
        self.assertNotEqual(a, jev.request_hash("m2", {"x": 1, "y": 2}, {"q": {"type": "noul", "instructions": "i"}}))

    def test_cache_hit_avoids_network_and_records_model(self):
        with tempfile.TemporaryDirectory() as d:
            cache = jev.Cache(Path(d))
            calls = []

            def fake_post(model, state, questions, key):
                calls.append(model)
                return {"model": "jev-9.9.9", "answers": {"q": {"type": "noul", "noul": 0.42}}, "usage": {"input_tokens": 10, "output_tokens": 1}}

            orig = jev._post
            jev._post = fake_post
            try:
                g = jev.Jev(cache, model="jev-x")
                g.key = "test-key"
                ans1 = g.ask({"s": 1}, {"q": jev.noul("i")})
                ans2 = g.ask({"s": 1}, {"q": jev.noul("i")})
            finally:
                jev._post = orig
            self.assertEqual(ans1, ans2)
            self.assertEqual(calls, ["jev-x"])
            self.assertEqual(jev.answered_models(cache), {"jev-9.9.9": 1})
            rec = json.loads(next(cache.answers.glob("*.json")).read_text())
            self.assertEqual(rec["requested_model"], "jev-x")
            self.assertEqual(rec["answered_model"], "jev-9.9.9")

    def test_no_key_writes_pending_and_raises(self):
        with tempfile.TemporaryDirectory() as d:
            cache = jev.Cache(Path(d))
            g = jev.Jev(cache, model="jev-x")
            g.key = None
            with self.assertRaises(jev.NoGrader):
                g.ask({"s": 1}, {"q": jev.noul("i")})
            self.assertEqual(cache.pending_count(), 1)
            pend = json.loads(next(cache.pending.glob("*.json")).read_text())
            # Answering in the documented shape clears the pending file on the next ask.
            cache.put(pend["hash"], {"hash": pend["hash"], "grader": "model-fallback", "answered_model": "model-fallback:test",
                                     "answers": {"q": {"type": "noul", "noul": 0.5}}})
            self.assertEqual(g.ask({"s": 1}, {"q": jev.noul("i")})["q"]["noul"], 0.5)
            self.assertEqual(cache.pending_count(), 0)


if __name__ == "__main__":
    unittest.main()
