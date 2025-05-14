import os, re, tempfile, git, yaml, shutil
from datetime import datetime, timedelta

# Setup
REPO_URL = "https://github.com/ethereum/EIPs.git"
TMP_DIR = tempfile.mkdtemp()
REPO_PATH = os.path.join(TMP_DIR, "EIPs")
START_DATE = datetime.utcnow() - timedelta(days=7)

# Clone the repo
repo = git.Repo.clone_from(REPO_URL, REPO_PATH)
eip_dir = os.path.join(REPO_PATH, "EIPS")

# Track file last commit dates
file_commit_dates = {}
for commit in repo.iter_commits(paths="EIPS", max_count=1000):
    for f in commit.stats.files:
        if f.startswith("EIPS/EIP-") and f.endswith(".md") and f not in file_commit_dates:
            file_commit_dates[f] = datetime.utcfromtimestamp(commit.committed_date)

# Extract valid EIPs modified in past 7 days
eips = []
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
                if isinstance(metadata, dict) and metadata.get("status") in ["Draft", "Final", "Last Call", "Review"]:
                    eip_number = metadata["eip"]
                    eips.append(f"- [{metadata['title']}](https://eips.ethereum.org/EIPS/eip-{eip_number}) ({metadata['status']}) – updated {commit_date.strftime('%Y-%m-%d')}")
            except yaml.YAMLError:
                pass

# Output to context file
os.makedirs("context", exist_ok=True)
with open("context/context_eips.md", "w") as out:
    out.write("## EIPs & Standards\n\n")
    out.write("\n".join(eips) if eips else "No new or updated EIPs in the past 7 days.\n")

shutil.rmtree(TMP_DIR)
