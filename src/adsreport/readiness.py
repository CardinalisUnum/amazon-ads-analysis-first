"""Local readiness without network calls, credential output or automatic delivery."""

from pathlib import Path

from adsreport.ai.commentary import credentials
from adsreport.config import load_config
from adsreport.notifications import readiness, settings
from adsreport.render.pdf import render_pdf


def check_readiness(config_dir: Path) -> dict[str, object]:
    result: dict[str, object] = {}
    try:
        load_config(config_dir)
        result["configuration"] = "ready"
    except ValueError:
        result["configuration"] = "needs_setup"
    try:
        render_pdf(b"<p>SAMPLE DATA local PDF readiness check</p>")
        result["pdf_native_libraries"] = "ready"
    except (ValueError, OSError):
        result["pdf_native_libraries"] = "needs_setup"
    try:
        key, confirmed = credentials(Path(".env"))
        result["ai_credentials_configured"] = bool(key and confirmed)
    except OSError:
        result["ai_credentials_configured"] = False
    try:
        result["notifications"] = readiness(settings())
    except OSError:
        result["notifications"] = {"enabled": False, "email": False, "discord": False}
    result["local_reporting_ready"] = (
        result["configuration"] == "ready" and result["pdf_native_libraries"] == "ready"
    )
    result["ai_note"] = (
        "Configuration only. Access/quota is not probed; templates work offline."
    )
    return result
