import sys
import subprocess
import time
import argparse


def start_backend():
    """Launches FastAPI backend server using uvicorn."""
    print("🚀 Starting FastAPI backend on http://127.0.0.1:8000...")
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])


def start_frontend():
    """Launches Streamlit frontend server."""
    print("🎨 Starting Streamlit frontend on http://localhost:8501...")
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])


def main():
    parser = argparse.ArgumentParser(description="AI Career Intelligence Application Launcher")
    parser.add_argument("--backend", action="store_true", help="Start only FastAPI backend server")
    parser.add_argument("--frontend", action="store_true", help="Start only Streamlit frontend server")
    args = parser.parse_args()

    # If neither flag specified, run both by default
    run_all = not (args.backend or args.frontend)

    processes = []
    try:
        if args.backend or run_all:
            p_backend = start_backend()
            processes.append(p_backend)
            time.sleep(2)  # Give backend time to initialize DB

        if args.frontend or run_all:
            p_frontend = start_frontend()
            processes.append(p_frontend)

        print("Press Ctrl+C to stop servers...")
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\nStopping servers...")
        for p in processes:
            p.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
