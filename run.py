"""Development server entry point."""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Tea API running at http://localhost:{port}")
    print(f"   TIF signature: http://localhost:{port}/brew")
    app.run(host="0.0.0.0", port=port, debug=True)
