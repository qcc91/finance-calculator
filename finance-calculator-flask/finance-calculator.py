import os

from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("API_HOST", "localhost"),
        port=int(os.getenv("API_PORT", "3000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
