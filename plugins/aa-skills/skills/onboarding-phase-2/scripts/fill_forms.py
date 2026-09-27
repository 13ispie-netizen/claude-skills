"""Fill the DE 34 (CA) or PFL pay deduction notice (NY) and upload it to Drive.

DE 34:  fill_forms.py de34 --folder ID --name "Last, First" --first F --mi M --last L
            --street-num N --street-name S [--unit U] --city C --state ST --zip Z --start MMDDYY
PFL:    fill_forms.py pfl --folder ID --name "Last, First" --employee "First Last"
            --rate 34 --hours 7.5
        Hours = expected weekly hours from the offer letter (median of a range).
        A+A pays semi-monthly (15th + last day), so a pay period = 52/24 weeks.

SSN, FEIN, and the CA employer account # are always left blank for Erin.
Prints JSON with the Drive id and, for PFL, the local path for make_draft.py.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ASSETS, ensure_pypdf, upload_to_drive  # noqa: E402

ensure_pypdf()
from pypdf import PdfReader, PdfWriter  # noqa: E402

EMPLOYER = {
    "BUSINESS NAME:": "Architecture + Advocacy",
    "CONTACT PERSON:": "Erin Light",
    "PHONE NUMBER:": "323-391-3791",
    "ADDRESS (STREET, CITY, STATE, AND ZIP CODE):": "P.O. Box 18205, Los Angeles, CA 90018",
}
PFL_RATE = 0.00432
WEEKS_PER_PERIOD = 52 / 24


def dollars(x):
    return f"{round(x * 100) // 100:,}"


def cents(x):
    return f"{round(x * 100) % 100:02d}"


def fill(template, values, out):
    w = PdfWriter()
    w.append(PdfReader(str(template)))
    for page in w.pages:
        w.update_page_form_field_values(page, values, auto_regenerate=False)
    w.set_need_appearances_writer(True)
    with open(out, "wb") as fh:
        w.write(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("form", choices=["de34", "pfl"])
    ap.add_argument("--folder", required=True)
    ap.add_argument("--name", required=True, help='"Last, First" for the filename')
    for a in ["first", "mi", "last", "street-num", "street-name", "unit", "city", "state", "zip",
              "start", "employee"]:
        ap.add_argument(f"--{a}", default="")
    ap.add_argument("--rate", type=float)
    ap.add_argument("--hours", type=float)
    a = ap.parse_args()
    today = datetime.date.today()
    stamp = today.strftime("%y%m%d")
    result = {}

    if a.form == "de34":
        values = dict(EMPLOYER)
        values.update({
            "EMPLOYEE FIRST NAME (1):": a.first, "M I (1):": a.mi, "EMPLOYEE LAST NAME (1):": a.last,
            "STREET NUMBER (1):": a.street_num, "STREET NAME (1):": a.street_name,
            "UNIT/APT (1):": a.unit, "CITY (1):": a.city, "STATE (2 CHARACTERS) (1):": a.state,
            "ZIP CODE (1):": a.zip, "START-OF-WORK DATE (M M D D Y Y) (1):": a.start,
            "DATE (M M D D Y Y):": today.strftime("%m%d%y"),
        })
        out = Path.home() / ".cache" / f"{stamp}_DE34_{a.name}.pdf"
        fill(ASSETS / "de34.pdf", values, out)
    else:
        per_period = round(a.rate * a.hours * WEEKS_PER_PERIOD, 2)
        deduction = round(per_period * PFL_RATE, 2)
        values = {
            "Employee Name": a.employee, "Employer Name": "Architecture + Advocacy",
            "enter dollar amount1": dollars(per_period), "enter cents amount1": cents(per_period),
            "enter dollar amount2": dollars(deduction), "enter cents amount2": cents(deduction),
        }
        out = Path.home() / ".cache" / f"{stamp}_PFL-deduction-notice_{a.name}.pdf"
        fill(ASSETS / "pfl-pay-deduction-notice-2026.pdf", values, out)
        result.update({"pay_period_earnings": per_period, "pfl_deduction": deduction, "local_path": str(out)})

    result["drive_id"], result["status"] = upload_to_drive(out, a.folder, out.name)
    result["file"] = out.name
    if a.form == "de34":
        out.unlink()
    print(json.dumps(result))


if __name__ == "__main__":
    main()
