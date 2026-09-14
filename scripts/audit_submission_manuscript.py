# -*- coding: utf-8 -*-
"""Audit the publication manuscript against journal and evidence invariants."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / "reports/publication_value_of_information_2026-09-13"
MANUSCRIPT = PUBLICATION / "manuscript_v0.en.md"
BIBLIOGRAPHY = PUBLICATION / "references.bib"
E6_ANALYSIS = PUBLICATION / "confirmatory/e6/E6_analysis.json"
E6_SECONDARY = PUBLICATION / "confirmatory/e6/E6_secondary_and_mechanism.json"
T2_ANALYSIS = PUBLICATION / "confirmatory/t2rb/T2RB_analysis.json"
DEFAULT_OUTPUT = PUBLICATION / "submission/manuscript_submission_audit.json"

WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
PLACEHOLDER = re.compile(r"\[(?:Author|Insert)[^\]\n]+\]")


def words(text: str) -> list[str]:
    plain = re.sub(r"[`*_#]", " ", text)
    return WORD.findall(plain)


def section(text: str, start: str, end: str) -> str:
    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except IndexError as exc:
        raise ValueError(f"could not isolate section {start!r} to {end!r}") from exc


def bib_records(text: str) -> list[dict[str, str]]:
    records = []
    for match in re.finditer(r"@\w+\{[^,]+,(.*?)(?=\n\}\s*(?:\n@|\Z))", text, re.DOTALL):
        block = match.group(1)
        author = re.search(r"author\s*=\s*\{([^}]+)\}", block)
        year = re.search(r"year\s*=\s*\{(\d{4})\}", block)
        if author is None or year is None:
            raise ValueError("each bibliography record must contain author and year")
        first_author = author.group(1).split(" and ", 1)[0].split(",", 1)[0].strip()
        records.append({"surname": first_author, "year": year.group(1)})
    if not records:
        raise ValueError("no BibTeX records parsed")
    return records


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def audit() -> dict[str, object]:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    bibliography = BIBLIOGRAPHY.read_text(encoding="utf-8")
    e6 = json.loads(E6_ANALYSIS.read_text(encoding="utf-8"))
    e6_secondary = json.loads(E6_SECONDARY.read_text(encoding="utf-8"))
    t2 = json.loads(T2_ANALYSIS.read_text(encoding="utf-8"))

    abstract = section(manuscript, "## Abstract", "**Keywords:")
    scientific_text = section(manuscript, "## Abstract", "## References")
    gross_article = manuscript.split("## Figure captions", 1)[0]
    body_before_references = manuscript.split("## References", 1)[0]
    captions = manuscript.split("## Figure captions", 1)[1]
    keyword_match = re.search(r"\*\*Keywords:\*\*\s*(.+)", manuscript)
    if keyword_match is None:
        raise ValueError("missing Keywords line")
    keywords = [value.strip() for value in keyword_match.group(1).split(";") if value.strip()]

    failures: list[str] = []
    required_sections = (
        "## Abstract",
        "## 1. Introduction",
        "## 2. Methods",
        "## 3. Results",
        "## 4. Discussion",
        "## 5. Conclusion",
        "## Data and Code Availability",
        "## Supplementary Materials",
        "## Funding",
        "## Competing Interests",
        "## Ethics Statement",
        "## Author Contributions",
        "## Generative-AI Disclosure",
        "## References",
        "## Figure captions",
    )
    for heading in required_sections:
        require(heading in manuscript, f"missing required section: {heading}", failures)

    gross_words = len(words(gross_article))
    scientific_words = len(words(scientific_text))
    abstract_words = len(words(abstract))
    require(6000 <= gross_words <= 12000, f"gross article word count outside 6000-12000: {gross_words}", failures)
    require(150 <= abstract_words <= 250, f"abstract word count outside 150-250: {abstract_words}", failures)
    require(5 <= len(keywords) <= 6, f"keyword count outside 5-6: {len(keywords)}", failures)

    for figure_number in range(1, 6):
        require(
            re.search(rf"Figure {figure_number}(?:[A-B])?", body_before_references) is not None,
            f"Figure {figure_number} is not cited in the manuscript body",
            failures,
        )
        require(
            len(re.findall(rf"\*\*Figure {figure_number}\.", captions)) == 1,
            f"Figure {figure_number} caption is missing or duplicated",
            failures,
        )

    bibliography_records = bib_records(bibliography)
    reference_section = section(manuscript, "## References", "## Figure captions")
    uncited = []
    missing_from_reference_list = []
    for record in bibliography_records:
        surname, year = record["surname"], record["year"]
        citation_pattern = rf"{re.escape(surname)}(?: et al\.)?[^\n()]{{0,80}}\({year}\)|{re.escape(surname)}(?: et al\.)?, {year}"
        if re.search(citation_pattern, body_before_references) is None:
            uncited.append(f"{surname} {year}")
        if surname not in reference_section or year not in reference_section:
            missing_from_reference_list.append(f"{surname} {year}")
    require(not uncited, f"bibliography entries not cited: {uncited}", failures)
    require(
        not missing_from_reference_list,
        f"BibTeX entries missing from manuscript reference list: {missing_from_reference_list}",
        failures,
    )

    slope = e6["primary"]["slope_summary"]["mean"]
    slope_ci = e6["primary"]["t_ci95"]
    slope_p = e6["primary"]["p"]
    required_fragments = [
        f"{slope:.3f}",
        f"{slope_ci['low']:.3f} to {slope_ci['high']:.3f}",
        f"p={slope_p:.4f}",
        "Eighteen of 30 slopes were positive and 12 were negative",
    ]
    for row in e6_secondary["by_realized_fruit_energy"]:
        value = row["B2_minus_B3"]["paired_difference"]["mean"]
        required_fragments.append(f"{value:+.3f}")
    primary = t2["primary"]["paired_difference"]
    secondary = t2["direct_replication_secondary"]["paired_difference"]
    required_fragments.extend(
        [
            f"{primary['mean']:.3f}",
            f"{primary['t_ci95']['low']:.3f} to {primary['t_ci95']['high']:.3f}",
            f"p={primary['p']:.6f}",
            f"{secondary['mean']:.3f}",
            f"{secondary['t_ci95']['low']:.3f} to {secondary['t_ci95']['high']:.3f}",
            f"p={secondary['p']:.6f}",
        ]
    )
    for fragment in required_fragments:
        require(fragment in manuscript, f"evidence-bound numeric text missing: {fragment}", failures)

    disallowed_phrases = (
        "indistinguishable from zero at 10",
        "dose-matched observable toxicity",
        "a supplied heritable trait",
        "independent reproduction was completed",
    )
    for phrase in disallowed_phrases:
        require(phrase not in manuscript, f"unsupported or imprecise phrase remains: {phrase}", failures)

    placeholders = sorted(set(PLACEHOLDER.findall(manuscript)))
    expected_author_actions = (
        "public archive citation/DOI/code-release tag",
        "funding statement",
        "competing-interest statement",
        "ethics confirmation",
        "author-contribution statement",
        "AI-disclosure approval and any additional AI use",
    )
    return {
        "schema_version": 1,
        "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
        "automated_scientific_checks": "PASS" if not failures else "FAIL",
        "submission_ready": not failures and not placeholders,
        "word_counts": {
            "gross_article_through_declarations_and_references": gross_words,
            "abstract": abstract_words,
            "scientific_text_abstract_through_declarations": scientific_words,
        },
        "keywords": keywords,
        "figures": 5,
        "bibliography_entries": len(bibliography_records),
        "unresolved_placeholders": placeholders,
        "author_actions_expected": list(expected_author_actions),
        "failures": failures,
        "evidence_sources": [
            E6_ANALYSIS.relative_to(ROOT).as_posix(),
            E6_SECONDARY.relative_to(ROOT).as_posix(),
            T2_ANALYSIS.relative_to(ROOT).as_posix(),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--strict-submission-ready", action="store_true")
    args = parser.parse_args()
    result = audit()
    output = Path(args.out)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(
        f"{result['automated_scientific_checks']}: {result['word_counts']['gross_article_through_declarations_and_references']} gross words, "
        f"{len(result['keywords'])} keywords, {result['figures']} figures, "
        f"{result['bibliography_entries']} bibliography entries, "
        f"{len(result['unresolved_placeholders'])} unresolved placeholders"
    )
    if result["automated_scientific_checks"] != "PASS":
        return 1
    if args.strict_submission_ready and not result["submission_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
