"""
Generate the synthetic study documents in samples/documents/ and copy them
into the upload scenarios in samples/scenarios/.

Every document is fictional, labelled SYNTHETIC, and contains no patient data.
Re-run after editing: python scripts/make_synthetic_pdfs.py
"""

import shutil
from pathlib import Path

from fpdf import FPDF

SAMPLES = Path(__file__).resolve().parents[1] / "samples"
OUT = SAMPLES / "documents"
FINAL_SET = [
    "protocol-v1.pdf",
    "device-verification-results.pdf",
    "adverse-event-reconciliation.pdf",
    "site-completion-summary.pdf",
]
SCENARIOS = {
    "1-ready": FINAL_SET + ["facilities-parking-memo.pdf"],
    "2-missing-adverse-event": [n for n in FINAL_SET if "adverse" not in n],
    "3-draft-adverse-event": [n.replace("reconciliation.pdf", "reconciliation-draft.pdf") for n in FINAL_SET],
}

BANNER = "SYNTHETIC TEST DOCUMENT - FICTIONAL DATA - NOT FOR CLINICAL USE"

DOCUMENTS = {
    "protocol-v1.pdf": (
        "Clinical Study Protocol - Version 1.0",
        [
            "Study: SYN-CEC-DOC (Synthetic Device Performance Study)",
            "Document status: FINAL - approved by synthetic study sponsor on 2026-01-15.",
            "Section 1. Objectives: evaluate the performance of the synthetic device model SD-100.",
            "Section 2. Study design: single-arm, three synthetic sites, 60 synthetic participants.",
            "Section 3. Endpoints and schedule of assessments are defined in Appendix A.",
            "Section 4. Adverse event handling follows the sponsor safety management plan.",
        ],
    ),
    "device-verification-results.pdf": (
        "Device Verification Results Report",
        [
            "Device: synthetic device model SD-100, firmware 2.3.1.",
            "Document status: FINAL - signed by synthetic verification lead.",
            "Verification test suite VT-01 through VT-24 executed.",
            "Result: 24 of 24 verification tests passed acceptance criteria.",
            "Raw data files are archived under synthetic reference VR-2026-004.",
        ],
    ),
    "adverse-event-reconciliation.pdf": (
        "Adverse Event Reconciliation Record",
        [
            "Study: SYN-CEC-DOC.",
            "Document status: FINAL - reconciliation signed off by synthetic data manager.",
            "Reconciliation between the synthetic EDC and the synthetic safety database.",
            "Synthetic adverse event records compared: 12. Open discrepancies: 0.",
            "Reconciliation completed on 2026-03-02.",
        ],
    ),
    "adverse-event-reconciliation-draft.pdf": (
        "Adverse Event Reconciliation Record - DRAFT",
        [
            "Study: SYN-CEC-DOC.",
            "Document status: DRAFT - pending data manager sign-off.",
            "Reconciliation between the synthetic EDC and the synthetic safety database.",
            "Synthetic adverse event records compared: 9 of 12. Open discrepancies: 3.",
            "Remaining records to be reconciled before sign-off.",
        ],
    ),
    "site-completion-summary.pdf": (
        "Site Completion Summary",
        [
            "Study: SYN-CEC-DOC.",
            "Document status: FINAL - approved by synthetic clinical operations lead.",
            "Synthetic sites closed: 3 of 3.",
            "Close-out visits completed for all synthetic sites.",
        ],
    ),
    "facilities-parking-memo.pdf": (
        "Facilities Memo - Parking Update",
        [
            "Document status: FINAL.",
            "The north parking lot will be resurfaced during the week of 2026-04-06.",
            "Staff should use the south lot during this period.",
        ],
    ),
}


def build(title: str, lines: list[str]) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 8, BANNER, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    for line in lines:
        pdf.multi_cell(0, 7, line, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (title, lines) in DOCUMENTS.items():
        (OUT / name).write_bytes(build(title, lines))
        print(OUT / name)
    for scenario, names in SCENARIOS.items():
        folder = SAMPLES / "scenarios" / scenario
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
        for name in names:
            shutil.copy(OUT / name, folder / name)
        print(folder)


if __name__ == "__main__":
    main()
