"""Run background generation workers without serving HTTP."""

from app.services.generation_jobs import run_forever

if __name__ == "__main__":
    run_forever()
