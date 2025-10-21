# test_wkhtmltopdf.py
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
wkhtmltopdf_path = REPO_ROOT / "workspace" / "wkhtmltopdf" / "bin" / "wkhtmltopdf.exe"

print(f"Chemin testé: {wkhtmltopdf_path}")
print(f"Existe: {wkhtmltopdf_path.exists()}")

if wkhtmltopdf_path.exists():
    print("✅ wkhtmltopdf trouvé!")
else:
    print("❌ wkhtmltopdf non trouvé à cet emplacement")
