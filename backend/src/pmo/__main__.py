import logging
import os

from pmo.main import create_app, start_background_refresh

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
app = create_app()
start_background_refresh()
app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
