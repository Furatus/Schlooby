from dotenv import load_dotenv,find_dotenv
import sys

def load_env():
        # charger le .env
    try:
        find_dotenv(filename='.env',raise_error_if_not_found=True)
        load_dotenv()
    except Exception as e:
        print(f"Error loading .env file: {e}")
        sys.exit(1)