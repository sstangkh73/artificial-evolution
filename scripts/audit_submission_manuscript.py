# -*- coding: utf-8 -*-
"""Audit the publication manuscript against journal and evidence invariants.

The Markdown source is checked for evidence-bound numbers, citations, and author
placeholders. The built submission PDF is checked separately: the PDF builder
injects its own title-page fields and filters working-draft front matter, so a
clean Markdown source does not imply a clean PDF.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PUBLICATION = ROOT / "reports/publication_value_of_information_2026-09-13"
MANUSCRIPT = PUBLICATION / "manuscript_v0.en.md"
BIBLIOGRAPHY = PUBLICATION / "references.bib"
E6_ANALYSIS = PUBLICATION / "confirmatory/e6/E6_analysis.json"
E6_SECONDARY = PUBLICATION / "confirmatory/e6/E6_secondary_and_mechanism.json"
T2_ANALYSIS = PUBLICATION / "confirmatory/t2rb/T2RB_analysis.json"
MECHANISM_ANALYSIS = PUBLICATION / "revision_2026-09-15/derived/mechanism_analysis.json"
SUBMISSION_PDF = PUBLICATION / "submission/manuscript_initial_submission_draft.pdf"
DEFAULT_OUTPUT = PUBLICATION / "submission/manuscript_submission_audit.json"
AUTHOR_METADATA = (
    "Chisanupong Injun",
    "Deebuk Phangnga Wittayayon School",
    "Phang Nga 82000, Thailand",
    "chisanupong.injun@gmail.com",
    "https://orcid.org/0009-0000-2979-1916",
)

WORD = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
PLACEHOLDER = re.compile(r"\[(?:Author|Insert)[^\]\n]+\]")
# The PDF builder adds title-page fields that are absent from the Markdown.
# Match actionable markers rather than every bracketed span because statistical
# tables legitimately contain confidence intervals such as [-8.826, -2.037].
PDF_PLACEHOLDER = re.compile(
    r"\[(?:(?:Author|Insert)[^\]]+|Affiliation|Postal address|Email; corresponding author)\]"
)
# Working-draft front matter that must never reach the rendered manuscript.
INTERNAL_NOTE_MARKERS = (
    "Manuscript type:",
    "Target journal:",
    "Status:",
    "must be rechecked",
    "VECTOR_FIGURE_PAGE_",
)


def words(text: str) -> list[str]:
    plain = re.sub(r"</?sub>", " ", text)
    plain = re.sub(r"[`*_#]", " ", plain)
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
        journal = re.search(r"journal\s*=\s*\{([^}]+)\}", block)
        records.append({
            "surname": first_author,
            "year": year.group(1),
            "journal": journal.group(1) if journal else "",
        })
    if not records:
        raise ValueError("no BibTeX records parsed")
    return records


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def cites_record(text: str, surname: str, year: str) -> bool:
    """Recognize common APA narrative and parenthetical author-year forms."""
    pattern = rf"\b{re.escape(surname)}\b[^\n()]{{0,120}}(?:\({year}\)|,\s*{year}\b)"
    return re.search(pattern, text) is not None


def first_figure_citation_order(text: str) -> list[int]:
    """Return figure numbers in the order each is first cited in body text."""
    positions: dict[int, int] = {}
    for match in re.finditer(r"\bFigure\s+([1-9]\d*)(?:[A-Z])?\b", text):
        number = int(match.group(1))
        positions.setdefault(number, match.start())
    return [number for number, _ in sorted(positions.items(), key=lambda item: item[1])]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def rendered_markdown(text: str) -> str:
    """Approximate the builder's rendering, in which emphasis and code markers vanish."""
    return normalize_space(re.sub(r"[*`]", "", text))


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def pdf_placeholders(text: str) -> list[str]:
    return sorted({normalize_space(match.group(0)) for match in PDF_PLACEHOLDER.finditer(text)})


def pdf_internal_notes(text: str) -> list[str]:
    flat = normalize_space(text)
    return [marker for marker in INTERNAL_NOTE_MARKERS if marker in flat]


def audit_pdf_text(
    text: str,
    title: str,
    abstract: str,
    required_metadata: tuple[str, ...] = (),
) -> dict[str, object]:
    """Check extracted PDF text; a title or abstract mismatch means the PDF is stale."""
    flat = normalize_space(text)
    matches = rendered_markdown(title) in flat and rendered_markdown(abstract) in flat
    placeholders = pdf_placeholders(text)
    notes = pdf_internal_notes(text)
    missing_metadata = [value for value in required_metadata if normalize_space(value) not in flat]
    return {
        "status": "PASS" if matches and not placeholders and not notes and not missing_metadata else "FAIL",
        "matches_manuscript": matches,
        "unresolved_placeholders": placeholders,
        "internal_notes": notes,
        "missing_author_metadata": missing_metadata,
    }


def audit_pdf(
    path: Path,
    title: str,
    abstract: str,
    required_metadata: tuple[str, ...] = (),
) -> dict[str, object]:
    if not path.is_file():
        return {
            "path": display_path(path),
            "present": False,
            "status": "MISSING",
            "matches_manuscript": False,
            "unresolved_placeholders": [],
            "internal_notes": [],
            "missing_author_metadata": list(required_metadata),
        }
    reader = PdfReader(str(path))
    page_text = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(page_text)
    result: dict[str, object] = {"path": display_path(path), "present": True, "pages": len(reader.pages)}
    result.update(audit_pdf_text(text, title, abstract, required_metadata))
    figure_caption_pages = {
        str(number): next(
            (page_number for page_number, value in enumerate(page_text, 1) if f"Figure {number}." in value),
            None,
        )
        for number in range(1, 6)
    }
    references_page = next(
        (page_number for page_number, value in enumerate(page_text, 1) if re.search(r"(?:^|\n)References(?:\n|$)", value)),
        None,
    )
    figures_interleaved = (
        references_page is not None
        and all(page is not None and page < references_page for page in figure_caption_pages.values())
    )
    caption_page_order = [figure_caption_pages[str(number)] for number in range(1, 6)]
    figures_in_numerical_page_order = (
        all(page is not None for page in caption_page_order)
        and caption_page_order == sorted(caption_page_order)
    )
    results_page = next(
        (page_number for page_number, value in enumerate(page_text, 1) if re.search(r"(?:^|\n)3\. Results(?:\n|$)", value)),
        None,
    )
    figures_after_results_heading = (
        results_page is not None
        and all(page is not None and page > results_page for page in caption_page_order)
    )
    if not figures_in_numerical_page_order or not figures_after_results_heading:
        result["status"] = "FAIL"
    result["figure_caption_pages"] = figure_caption_pages
    result["references_page"] = references_page
    result["figures_interleaved_before_references"] = figures_interleaved
    result["figures_in_numerical_page_order"] = figures_in_numerical_page_order
    result["results_heading_page"] = results_page
    result["figures_after_results_heading"] = figures_after_results_heading
    if not figures_interleaved:
        result["status"] = "FAIL"
    return result


def audit(pdf_path: Path = SUBMISSION_PDF) -> dict[str, object]:
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    bibliography = BIBLIOGRAPHY.read_text(encoding="utf-8")
    e6 = json.loads(E6_ANALYSIS.read_text(encoding="utf-8"))
    e6_secondary = json.loads(E6_SECONDARY.read_text(encoding="utf-8"))
    t2 = json.loads(T2_ANALYSIS.read_text(encoding="utf-8"))
    mechanisms = json.loads(MECHANISM_ANALYSIS.read_text(encoding="utf-8"))

    title = manuscript.split("\n", 1)[0].lstrip("#").strip()
    abstract = section(manuscript, "## Abstract", "**Keywords:")
    scientific_text = section(manuscript, "## Abstract", "## References")
    core_article = section(manuscript, "## Abstract", "## Data and Code Availability")
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

    for value in AUTHOR_METADATA:
        require(value in manuscript, f"confirmed author metadata missing from manuscript source: {value}", failures)

    gross_words = len(words(gross_article))
    scientific_words = len(words(scientific_text))
    core_words = len(words(core_article))
    abstract_words = len(words(abstract))
    require(6000 <= gross_words <= 12000, f"gross article word count outside 6000-12000: {gross_words}", failures)
    require(
        6000 <= scientific_words <= 12000,
        f"conservative count excluding references and captions outside 6000-12000: {scientific_words}",
        failures,
    )
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

    citation_order = first_figure_citation_order(body_before_references)
    require(
        citation_order == [1, 2, 3, 4, 5],
        f"figures are first cited out of numerical order: {citation_order}",
        failures,
    )

    bibliography_records = bib_records(bibliography)
    artificial_life_entries = sum(
        record["journal"].strip().lower() == "artificial life"
        for record in bibliography_records
    )
    require(
        artificial_life_entries >= 5,
        f"fewer than five Artificial Life journal sources: {artificial_life_entries}",
        failures,
    )
    reference_section = section(manuscript, "## References", "## Figure captions")
    uncited = []
    missing_from_reference_list = []
    for record in bibliography_records:
        surname, year = record["surname"], record["year"]
        if not cites_record(body_before_references, surname, year):
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
    mechanism_slope = mechanisms["E6"]["slope"]
    leave_out_10 = next(
        row for row in mechanism_slope["leave_one_energy_out"]
        if row["excluded_energy"] == 10
    )
    required_fragments = [
        f"{slope:.3f}",
        f"{slope_ci['low']:.3f} to {slope_ci['high']:.3f}",
        f"p={slope_p:.4f}",
        f"SD {mechanism_slope['summary']['sd']:.3f}",
        f"{mechanism_slope['minimum_effect_sensitivity']['one_sided_monte_carlo_sign_flip_p']:.3f}",
        f"{leave_out_10['slope_summary']['mean']:.3f}",
        f"{leave_out_10['t_ci95']['low']:.3f} to {leave_out_10['t_ci95']['high']:.3f}",
    ]
    correlations = mechanisms["E6"]["within_arm_energy_cell_correlations_with_followup"]
    for metric in (
        "staple_meals_per_followup_tick",
        "toxin_excess_per_followup_tick",
        "fruit_meals_per_followup_tick",
        "toxin_excess_per_fruit_meal",
    ):
        required_fragments.append(f"{correlations[metric]:.3f}")
    for row in e6_secondary["by_realized_fruit_energy"]:
        for contrast_name in (
            "B2_minus_B3",
            "B2_minus_B1",
            "B3_minus_B1_descriptive",
        ):
            value = row[contrast_name]["paired_difference"]["mean"]
            required_fragments.append(f"{value:+.3f}")
        if row["realized_fruit_energy"] == 4:
            secondary_adjusted = row["B2_minus_B1"]["paired_difference"]["holm_adjusted_p"]
            required_fragments.append(f"{secondary_adjusted:.5f}")
    for contrast_name in ("A2-A3R", "A2-A3O"):
        contrast = next(
            row for row in mechanisms["T2RB"]["paired_contrasts"]
            if row["contrast"] == contrast_name
            and row["metric"] == "founder_mean_followup_ticks"
        )
        required_fragments.extend([
            f"{abs(contrast['paired_difference']['mean']):.3f}",
            f"{contrast['paired_t_ci95']['low']:.3f} to {contrast['paired_t_ci95']['high']:.3f}",
            f"*d*<sub>z</sub> = {contrast['paired_standardized_mean_difference_dz']:.3f}",
        ])
    for fragment in required_fragments:
        require(fragment in manuscript, f"evidence-bound numeric text missing: {fragment}", failures)

    disallowed_phrases = (
        "indistinguishable from zero at 10",
        "dose-matched observable toxicity",
        "a supplied heritable trait",
        "independent reproduction was completed",
        "Sasaki and Tokoro (1999)",
        "structural noise floor",
        "For this major revision",
        "red-team mechanism tables",
        "Supplementary Red-team Revision Tables",
        "H1.2",
        "H3.2",
        "Before revision",
        "the separate revision inventory",
        "accompanies this draft",
        "The working supplement",
        "is being rebuilt",
        "|0.1|",
    )
    for phrase in disallowed_phrases:
        require(phrase not in manuscript, f"unsupported or imprecise phrase remains: {phrase}", failures)

    source_placeholders = sorted(set(PLACEHOLDER.findall(manuscript)))
    pdf = audit_pdf(pdf_path, title, abstract, AUTHOR_METADATA)
    placeholders = sorted(set(source_placeholders) | set(pdf["unresolved_placeholders"]))
    expected_author_actions = (
        "public archive citation/DOI/code-release tag",
        "funding statement",
        "competing-interest statement",
        "ethics confirmation",
        "author-contribution statement",
        "AI-disclosure approval and any additional AI use",
    )
    return {
        "schema_version": 2,
        "manuscript": MANUSCRIPT.relative_to(ROOT).as_posix(),
        "automated_scientific_checks": "PASS" if not failures else "FAIL",
        "submission_ready": not failures and not placeholders and pdf["status"] == "PASS",
        "word_counts": {
            "gross_article_through_declarations_and_references": gross_words,
            "abstract": abstract_words,
            "conservative_abstract_through_declarations_excluding_references": scientific_words,
            "core_article_abstract_through_conclusion": core_words,
        },
        "keywords": keywords,
        "figures": 5,
        "bibliography_entries": len(bibliography_records),
        "artificial_life_journal_entries": artificial_life_entries,
        "unresolved_placeholders": placeholders,
        "source_markdown_placeholders": source_placeholders,
        "pdf": pdf,
        "author_actions_expected": list(expected_author_actions),
        "failures": failures,
        "evidence_sources": [
            E6_ANALYSIS.relative_to(ROOT).as_posix(),
            E6_SECONDARY.relative_to(ROOT).as_posix(),
            T2_ANALYSIS.relative_to(ROOT).as_posix(),
            MECHANISM_ANALYSIS.relative_to(ROOT).as_posix(),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--pdf", default=str(SUBMISSION_PDF), help="built submission PDF to check")
    parser.add_argument("--strict-submission-ready", action="store_true")
    args = parser.parse_args()
    pdf_path = Path(args.pdf)
    if not pdf_path.is_absolute():
        pdf_path = ROOT / pdf_path
    result = audit(pdf_path)
    output = Path(args.out)
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    pdf = result["pdf"]
    print(
        f"{result['automated_scientific_checks']}: {result['word_counts']['gross_article_through_declarations_and_references']} gross words, "
        f"{len(result['keywords'])} keywords, {result['figures']} figures, "
        f"{result['bibliography_entries']} bibliography entries "
        f"({result['artificial_life_journal_entries']} from Artificial Life), "
        f"{len(result['unresolved_placeholders'])} unresolved placeholders; "
        f"PDF {pdf['status']}: matches source={pdf['matches_manuscript']}, "
        f"{len(pdf['unresolved_placeholders'])} placeholders, {len(pdf['internal_notes'])} internal notes"
    )
    if result["automated_scientific_checks"] != "PASS":
        return 1
    if args.strict_submission_ready and not result["submission_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
