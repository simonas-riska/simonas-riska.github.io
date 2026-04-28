import pandas as pd
import re
from pathlib import Path
from datetime import date

# =========================
# CONFIG
# =========================

INPUT_FILE = "software_inventory.csv"   # change this
OUTPUT_DIR = "software_shadow_it_output"

COLUMN_SOFTWARE_NAME = "Software Name"
COLUMN_SOFTWARE_TYPE = "Software Type"
COLUMN_SOFTWARE_VERSION = "Software Update"
COLUMN_USER_OR_DEVICE = "NetBIOS Name"  # for now this acts as "user/device"

RARE_THRESHOLD = 5  # software installed on <= 5 users/devices

Path(OUTPUT_DIR).mkdir(exist_ok=True)


# =========================
# CLEANING FUNCTIONS
# =========================

def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_version(version):
    version = normalize_text(version)
    if not version:
        return ""

    version = version.strip()
    version = re.sub(r"^[vV]", "", version)
    return version


def remove_version_from_name(software_name, version):
    """
    Removes version string from Software Name if Software Update/version appears inside it.
    Keeps original software name separately.
    """
    name = normalize_text(software_name)
    version = clean_version(version)

    if not name or not version:
        return name

    patterns = [
        version,
        f"v{version}",
        f"V{version}",
        f"- {version}",
        f"({version})",
    ]

    cleaned = name
    for pattern in patterns:
        cleaned = cleaned.replace(pattern, "")

    # Remove duplicated spaces and trailing separators
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"[\s\-_()]+$", "", cleaned)

    return cleaned.strip()


def basic_name_normalization(name):
    """
    Light normalization only.
    Do not over-clean because software names are fragile.
    """
    name = normalize_text(name)

    name = re.sub(r"\s+", " ", name)
    name = name.strip(" -_")

    return name


# =========================
# LOAD LARGE CSV SAFELY
# =========================

def load_inventory(file_path):
    print("[+] Loading CSV...")

    chunks = []
    for chunk in pd.read_csv(file_path, chunksize=100_000, low_memory=False):
        needed_cols = [
            COLUMN_SOFTWARE_NAME,
            COLUMN_SOFTWARE_TYPE,
            COLUMN_SOFTWARE_VERSION,
            COLUMN_USER_OR_DEVICE,
        ]

        missing = [col for col in needed_cols if col not in chunk.columns]
        if missing:
            raise ValueError(f"Missing columns in CSV: {missing}")

        chunk = chunk[needed_cols].copy()
        chunks.append(chunk)

    df = pd.concat(chunks, ignore_index=True)

    print(f"[+] Loaded rows: {len(df):,}")
    return df


# =========================
# PHASE 1 — CLEAN INVENTORY
# =========================

def clean_inventory(df):
    print("[+] Cleaning inventory...")

    df["software_name_original"] = df[COLUMN_SOFTWARE_NAME].apply(normalize_text)
    df["software_type"] = df[COLUMN_SOFTWARE_TYPE].apply(normalize_text)
    df["version"] = df[COLUMN_SOFTWARE_VERSION].apply(clean_version)
    df["user_or_device"] = df[COLUMN_USER_OR_DEVICE].apply(normalize_text)

    df["software_name_clean"] = df.apply(
        lambda row: remove_version_from_name(
            row["software_name_original"],
            row["version"]
        ),
        axis=1
    )

    df["software_name_clean"] = df["software_name_clean"].apply(basic_name_normalization)

    # Remove rows without useful software name
    df = df[df["software_name_clean"] != ""].copy()

    return df


# =========================
# PHASE 2 — GROUP INVENTORY
# =========================

def create_grouped_reports(df):
    print("[+] Creating grouped reports...")

    # Software total count
    software_summary = (
        df.groupby(["software_name_clean", "software_type"], dropna=False)
        .agg(
            total_installations=("user_or_device", "count"),
            unique_users_or_devices=("user_or_device", "nunique"),
            versions=("version", lambda x: ", ".join(sorted(set(v for v in x if v))[:20])),
        )
        .reset_index()
        .sort_values(["unique_users_or_devices", "software_name_clean"], ascending=[True, True])
    )

    # Version breakdown per software
    version_breakdown = (
        df.groupby(["software_name_clean", "software_type", "version"], dropna=False)
        .agg(
            installations=("user_or_device", "count"),
            unique_users_or_devices=("user_or_device", "nunique"),
            users_or_devices=("user_or_device", lambda x: ", ".join(sorted(set(x))[:50])),
        )
        .reset_index()
        .sort_values(["software_name_clean", "unique_users_or_devices"], ascending=[True, False])
    )

    # Software type overview
    type_summary = (
        df.groupby("software_type", dropna=False)
        .agg(
            unique_software=("software_name_clean", "nunique"),
            total_installations=("software_name_clean", "count"),
            unique_users_or_devices=("user_or_device", "nunique"),
        )
        .reset_index()
        .sort_values("total_installations", ascending=False)
    )

    # Rare software
    rare_software = software_summary[
        software_summary["unique_users_or_devices"] <= RARE_THRESHOLD
    ].copy()

    return software_summary, version_breakdown, type_summary, rare_software


# =========================
# PHASE 5 — LLM RESEARCH PLACEHOLDER
# =========================

def prepare_llm_research_queue(rare_software):
    print("[+] Preparing LLM research queue...")

    queue = rare_software.copy()

    queue["llm_status"] = "pending"
    queue["likely_vendor"] = ""
    queue["what_it_is"] = ""
    queue["enterprise_legitimacy"] = ""
    queue["security_relevance"] = ""
    queue["dual_use_capability"] = ""
    queue["risk_category"] = ""
    queue["recommendation"] = ""
    queue["confidence"] = ""
    queue["sources"] = ""

    return queue


# Uncomment and adapt later when API key is available.
#
# from openai import OpenAI
# client = OpenAI(api_key="YOUR_API_KEY")
#
# def research_software_with_llm(software_name, software_type, install_count):
#     prompt = f"""
# Research this software using web search.
#
# Software name: {software_name}
# Software type from inventory: {software_type}
# Install count: {install_count}
#
# Return JSON:
# {{
#   "software_name": "",
#   "likely_vendor": "",
#   "official_website": "",
#   "what_it_is": "",
#   "enterprise_legitimacy": "common / uncommon / suspicious / unknown",
#   "security_relevance": "",
#   "dual_use_capability": true,
#   "risk_category": [],
#   "recommendation": "allow / allow_with_justification / review / remove_if_unapproved",
#   "confidence": "low / medium / high",
#   "sources": []
# }}
#
# Rules:
# - Use web search.
# - Prefer official vendor pages.
# - Do not guess if unclear.
# - If sources are weak, mark confidence low.
# """
#
#     response = client.responses.create(
#         model="gpt-4.1",
#         tools=[{"type": "web_search_preview"}],
#         input=prompt
#     )
#
#     return response.output_text


# =========================
# PHASE 6 — JUSTIFICATION MESSAGE TEMPLATE
# =========================

def generate_justification_message(row):
    software = row["software_name_clean"]
    software_type = row["software_type"]
    deadline = "[INSERT DATE]"

    return f"""Hi [Name],

As part of a software inventory review, we identified the following application installed on your device:

Software: {software}
Software type: {software_type}

Could you please confirm whether this software is required for your role and provide a short business justification by {deadline}?

If the software is no longer needed or was not intentionally installed, please let us know so it can be reviewed for removal.

Thank you."""


def add_justification_messages(llm_queue):
    llm_queue["user_justification_message"] = llm_queue.apply(
        generate_justification_message,
        axis=1
    )

    return llm_queue


# =========================
# EXPORT
# =========================

def export_reports(df, software_summary, version_breakdown, type_summary, rare_software, llm_queue):
    output_file = Path(OUTPUT_DIR) / f"software_shadow_it_report_{date.today()}.xlsx"

    print(f"[+] Exporting Excel report: {output_file}")

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Clean Inventory", index=False)
        software_summary.to_excel(writer, sheet_name="Software Summary", index=False)
        version_breakdown.to_excel(writer, sheet_name="Version Breakdown", index=False)
        type_summary.to_excel(writer, sheet_name="Software Type Summary", index=False)
        rare_software.to_excel(writer, sheet_name="Rare Software", index=False)
        llm_queue.to_excel(writer, sheet_name="LLM Research Queue", index=False)

    print("[+] Done.")
    return output_file


# =========================
# MAIN
# =========================

def main():
    df_raw = load_inventory(INPUT_FILE)

    df_clean = clean_inventory(df_raw)

    software_summary, version_breakdown, type_summary, rare_software = create_grouped_reports(df_clean)

    llm_queue = prepare_llm_research_queue(rare_software)

    llm_queue = add_justification_messages(llm_queue)

    output_file = export_reports(
        df_clean,
        software_summary,
        version_breakdown,
        type_summary,
        rare_software,
        llm_queue
    )

    print(f"[+] Report created: {output_file}")


if __name__ == "__main__":
    main()
