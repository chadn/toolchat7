import sys
sys.path.append('./src/')
#print(sys.path)

"""
Entry point for the Streamlit application.
Simply imports and runs the main app from src.
"""
from src.streamlit_app import main

if __name__ == "__main__":
    main() 