import subprocess
import sys
from tqdm import tqdm
import requests
import time

def check_internet_connection():
    try:
        requests.get("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def upgrade_medicafe(package):
    try:
        # Check internet connection
        if not check_internet_connection():
            print("Error: No internet connection detected. Please check your internet connection and try again.")
            sys.exit(1)
        
        total_progress = 200  # Total progress for two runs
        
        with tqdm(total=total_progress, desc="Upgrading %s" % package, unit="%") as progress_bar:
            stdout_accumulator = b""
            stderr_accumulator = b""
            
            for _ in range(2):  # Run pip install twice
                process = subprocess.Popen([sys.executable, '-m', 'pip', 'install', '--upgrade', package, '--no-cache-dir', '--disable-pip-version-check', '--no-deps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                stdout_accumulator += stdout
                stderr_accumulator += stderr
                
                if process.returncode != 0:
                    # If the return code is non-zero, print error details
                    print("Error: Upgrade failed. Details:")
                    print("stdout:", stdout)
                    print("stderr:", stderr)
                    sys.exit(1)
                
                progress_bar.update(total_progress // 2)  # Update progress bar
                
                # Add a 3-second sleep between runs
                time.sleep(3)
                
            progress_bar.update(total_progress // 2)  # Update progress bar
            print("stdout:", stdout_accumulator.decode("utf-8"))
            print("stderr:", stderr_accumulator.decode("utf-8"))
            time.sleep(1)
    except Exception as e:
        # Log any other exceptions
        print("Error:", e)
        time.sleep(3)
        sys.exit(1)

if __name__ == "__main__":
    medicafe_package = "medicafe"
    upgrade_medicafe(medicafe_package)
