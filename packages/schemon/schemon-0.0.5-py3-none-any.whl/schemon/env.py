import os
from dotenv import load_dotenv

def loadenv():
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Construct the path to the .env file
    env_path = os.path.join(current_dir, '.env')
    
    # Load environment variables from the .env file
    load_dotenv(dotenv_path=env_path)