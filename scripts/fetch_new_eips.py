```python
import os, re, tempfile, git, yaml, shutil

REPO_URL = "https://github.com/ethereum/EIPs.git"
TMP_DIR = tempfile.mkdtemp()
REPO_PATH = os.path.join(TMP_DIR, "EIPs")

# Clone repo
repo = git.Repo.clone_from(REPO_URL, REPO_PATH)
eip_dir = os.path.join(REPO_PATH, "EIPS")

eips = []
for filename in os.listdir(eip_dir):
    if filename.endswith(".md"):
        with open(os.path.join(eip_dir, filename), "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                try:
                    metadata = yaml.safe_load(match.group(1))
                    if "eip" in metadata and metadata.get("status") in ["Draft", "Final", "Last Call", "Review"]:
                        eips.append({
                            "eip": metadata["eip"],
                            "title": metadata["title"],
                            "status": metadata["status"],
                        })
                except yaml.YAMLError:
                    continue

# Format to markdown
eips.sort(key=lambda x: int(x["eip"]))
lines = ["## EIPs & Standards\n"]
for e in eips:
    link = f"https://eips.ethereum.org/EIPS/eip-{e['eip']}"
    lines.append(f"- [{e['title']}]({link}) ({e['status']})")

# Write to context file
os.makedirs("context", exist_ok=True)
with open("context/context_eips.md", "w") as f:
    f.write("\n".join(lines))

shutil.rmtree(TMP_DIR)
