---
name: set-up-rfp
description: "Scaffold a new RFP go/no-go project kit in A+A's Contracted Work drive: fiscal-year project folder, subfolders, the RFP source files, a filled Project Quick Facts sheet, and a Gut Check copy. Use whenever Erin is invited to an RFP/RFSQ and wants to start the process, says 'set up an RFP', 'start a new RFP', 'new go/no-go', 'kick off the RFP', or drops RFP documents and wants the full project folder built. This is the front door for a new opportunity; it hands the quick-facts step to the rfp-quick-facts skill."
---

# Set Up an RFP

Builds the complete go/no-go kit for a new RFP/RFSQ in the **Contracted Work** shared drive, so the board can evaluate the opportunity. Creates the folder structure, files the source RFP, produces the Project Quick Facts sheet, and drops in a Gut Check copy.

---

## KEY RESOURCES (Contracted Work shared drive)

- **Drive root:** `0AF9x6YLZ2jSVUk9PVA` — holds one folder per fiscal year (`24-25`, `25-26`, `26-27`, ...).
- **Quick Facts template:** `1pbk38wUwLXUMOGD--5tGxsD60tj6VNc0ti4SaDK9Z6o` ("TEMPLATE Project Quick Facts").
- **Gut Check template:** `1T2oOGsjNLYl5GfXuLnWecb_R9oSIfp4vY_-U9QaQjJo` ("A+A Gut Check Questions").
- **Go/No-Go RFP Process (reference):** `1h3nSxZlbwUSk-x1K7XOQuXCmiWKRybMfQVSidffJnpI`.
- **Black-Listed / Red-Flag Firms sheet:** `18qG_uvq-bDnAigmCzf20TSPUAGJb9dr58dGcYuhQpm8`.

All operations are on a **shared drive** — set `supportsAllDrives=true` (and `includeItemsFromAllDrives=true` on searches) for every Drive call. In Claude Code use the `gws` CLI; degrade gracefully to whatever Drive tools the environment offers.

---

## WORKFLOW

### 0. Gather inputs
Confirm the **project name** (exact spelling, used in folder names) and get the **RFP + supporting documents** (files or a source folder). Ask if either is missing. Never guess the project name.

### 1. Find/create the fiscal-year folder
A+A's fiscal year runs **July 1 - June 30**, named `YY-YY` (e.g. `26-27` = Jul 2026 - Jun 2027). Compute the current FY from today's date: if month >= July, FY = `YY-(YY+1)`; else `(YY-1)-YY`. Look for that folder under the Drive root; **create it if it does not exist**. Confirm the FY with Erin if the opportunity spans a rollover.

### 2. Create the project folder + subfolders
Inside the FY folder, create a folder named `[Project Name]`. Inside it, create exactly two subfolders:
- `00. RFP + Contract`
- `[Project Name] go/no-go documents`

(Create a folder via `gws drive files create` with `mimeType: application/vnd.google-apps.folder` and the parent in `parents`.)

### 3. File the source RFP
Upload the RFP and all supporting documents into **`00. RFP + Contract`**.

### 4. Project Quick Facts sheet -> invoke `rfp-quick-facts`
Run the **rfp-quick-facts** skill. Tell it: the RFP source files are in `00. RFP + Contract`, and the filled copy of the Quick Facts template goes into the **`[Project Name] go/no-go documents`** folder. That skill reads the RFP in full and fills + brands the sheet.

### 5. Gut Check copy
Copy the Gut Check template into **`[Project Name] go/no-go documents`**, named `[Project Name] Gut Check`. **Do not fill it** - it is a live board discussion tool, worked through with the team, not by Claude.

### 6. Blacklist / red-flag check
Check the issuing organization and any named partners against the **Black-Listed / Red-Flag Firms** sheet. Report any match to Erin **in chat** (not in any doc).

### 7. Hand off
Give Erin links to: the project folder, the Quick Facts sheet, and the Gut Check. Then, **in chat only**, surface the initial go/no-go read: biggest risks, insurance gaps (from Quick Facts), blacklist hits, and anything that would trigger board approval (new partner, or a contract worth more than 10% of A+A's annual budget - both require board sign-off per the Go/No-Go process).

---

## NOTES

- **Document placement:** go/no-go decision docs (Quick Facts, Gut Check) live in `[Project Name] go/no-go documents`; the source RFP and eventual contract live in `00. RFP + Contract`.
- Do not fill the Gut Check; do fill the Quick Facts (via rfp-quick-facts).
- Keep naming exact; the go/no-go subfolder name literally includes "go/no-go documents".
- Confirm before creating anything if the project folder already exists (avoid duplicates).
