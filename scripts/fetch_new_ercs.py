import os
import re
import tempfile
import git
import yaml
import shutil
from datetime import datetime, timedelta

# === Step 1: Config ===
REPO_URL = "https://github.com/ethereum/ERCs.git"
TMP_DIR = tempfile.mkdtemp()
REPO_PATH = os.path.join(TMP_DIR, "ERCs")
START_DATE = datetime.utcnow() - timedelta(days=7)

# === Step 2: Clone repo ===
repo = git.Repo.clone_from(REPO_URL, REPO_PATH)
erc_dir = os.path.join(REPO_PATH, "ERCS")

# === Step 3: Get commit dates for files ===
file_commit_dates = {}
for commit in repo.iter_commits(paths="ERCS", max_count=1000):
    for f in commit.stats.files:
        if f.startswith("ERCS/") and f.endswith(".md") and f not in file_commit_dates:
            file_commit_dates[f] = datetime.utcfromtimestamp(commit.committed_date)

# === Step 4: Extract and filter ERC metadata ===
ercs = []
for filepath, commit_date in file_commit_dates.items():
    if commit_date < START_DATE:
        continue

    full_path = os.path.join(REPO_PATH, filepath)
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                metadata = yaml.safe_load(match.group(1))
                if metadata.get("type", "").upper() == "ERC":
                    erc_number = metadata["eip"]
                    ercs.append(f"- [{metadata['title']}](https://eips.ethereum.org/EIPS/eip-{erc_number}) ({metadata['status']}) – updated {commit_date.strftime('%Y-%m-%d')}")
            except Exception:
                continue

# === Step 5: Output to context file ===
os.makedirs("context", exist_ok=True)
output_path = "context/context_ercs.md"

with open(output_path, "w") as out:
    out.write("## ERCs (Ethereum Request for Comments)\n\n")
    if ercs:
        out.write("\n".join(sorted(ercs)))
    else:
        out.write("No new or updated ERCs in the past 7 days.\n")

# === Step 6: Cleanup ===
shutil.rmtree(TMP_DIR)
