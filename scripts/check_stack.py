"""P0 compatibility probe, separate from the report application's test suite."""

import importlib
import importlib.metadata
import json
import platform
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
import yaml
from google import genai

rows = json.loads(
    Path("docs/evidence/p0-package-metadata.json").read_text(encoding="utf-8-sig")
)
versions = {}
for row in rows:
    if row["name"] != "uv":
        versions[row["name"]] = importlib.metadata.version(row["name"])
for module in [
    "pydantic",
    "matplotlib",
    "xlsxwriter",
    "jinja2",
    "pptx",
    "pytest",
    "hypothesis",
    "mypy",
]:
    importlib.import_module(module)
frame = pd.DataFrame({"name": ["sample"], "amount": [1.0]})
pa.DataFrameSchema({"name": pa.Column(str), "amount": pa.Column(float)}).validate(frame)
copied = frame.copy(deep=False)
copied.loc[0, "amount"] = 2.0
assert frame.loc[0, "amount"] == 1.0
mapping = yaml.safe_load(Path("config/column_map.yaml").read_text(encoding="utf-8"))
assert "Sales (promoted)" in mapping["ads"]["promoted_sales"]
assert "Sales" in mapping["ads"]["ad_sales"]
with genai.Client(api_key="placeholder-no-request") as client:
    assert callable(client.interactions.create)
result = {
    "python": platform.python_version(),
    "versions": versions,
    "pandera_pandas_compatibility": "validated sample frame",
    "pandas_copy_on_write": "original preserved on shallow-copy modification",
    "string_dtype": str(frame["name"].dtype),
    "column_map": "distinct total and promoted aliases parsed",
    "sdk_shape": "interactions.create exists; no network request in this check",
}
try:
    from weasyprint import HTML

    pdf = HTML(string="<p>SAMPLE DATA - P0 native dependency check</p>").write_pdf()
    assert pdf.startswith(b"%PDF")
    result["pdf_native"] = "minimal PDF rendered"
except (ImportError, OSError) as exc:
    result["pdf_native"] = {
        "status": "native dependency unavailable",
        "error_type": type(exc).__name__,
    }
Path("docs/evidence/p0-stack.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, indent=2))
