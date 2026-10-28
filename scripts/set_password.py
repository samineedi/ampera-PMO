"""Set the login password in .env:  python scripts/set_password.py <new-password>"""
import re
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash

if len(sys.argv) != 2:
    raise SystemExit(__doc__)
env = Path(__file__).resolve().parents[1] / ".env"
text = env.read_text(encoding="utf-8")
line = "APP_PASSWORD_HASH=" + generate_password_hash(sys.argv[1])
text = re.sub(r"(?m)^APP_PASSWORD_HASH=.*$", lambda m: line, text) if re.search(r"(?m)^APP_PASSWORD_HASH=", text) else text + "\n" + line + "\n"
env.write_text(text, encoding="utf-8")
print("Password updated. Restart the app to apply.")
