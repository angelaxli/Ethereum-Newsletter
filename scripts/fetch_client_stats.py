import requests
from bs4 import BeautifulSoup

url = "https://clientdiversity.org"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

output = ["## ⚠️ Centralization Watch"]

# Look for the Lido stat
for tag in soup.find_all("div"):
    if "Lido" in tag.text and "%" in tag.text:
        output.append(f"- 🛑 {tag.text.strip()}")
        break

# Execution Layer Stats
output.append("\n### Execution Layer Client Diversity")
for tag in soup.find_all("ul"):
    if "Execution layer" in tag.previous_sibling.get_text():
        for li in tag.find_all("li"):
            output.append(f"- {li.text.strip()}")

# Consensus Layer Stats
output.append("\n### Consensus Layer Client Diversity")
for tag in soup.find_all("ul"):
    if "Consensus layer" in tag.previous_sibling.get_text():
        for li in tag.find_all("li"):
            output.append(f"- {li.text.strip()}")

# Save to file
with open("context_stats.md", "w") as f:
    f.write("\n".join(output))
