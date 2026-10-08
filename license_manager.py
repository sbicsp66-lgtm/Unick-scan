import subprocess
import requests

class LicenseManager:
    def __init__(self):
        # আপাতত লোকাল সার্ভার লিংক, পরবর্তীতে Railway-এর ডেপ্লয় করা লিংক এখানে বসবে
        self.api_url = "http://localhost:5000/api" 

    def get_machine_id(self):
        try:
            # মাদারবোর্ডের ইউনিক UUID বের করা
            output = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
            return output
        except Exception:
            return "UNKNOWN-MACHINE-ID"

    def check_trial_status(self):
        machine_id = self.get_machine_id()
        try:
            response = requests.post(f"{self.api_url}/check-status", json={"machine_id": machine_id})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "active":
                    return True, "Activated"
                elif data.get("status") == "trial":
                    return True, data.get("days_left")
                else:
                    return False, 0 # Expired or Blocked
            return False, "Server Error"
        except Exception as e:
            print("API Connection Error:", e)
            return False, "Server Offline/No Internet"

    def activate_license(self, license_key):
        machine_id = self.get_machine_id()
        try:
            response = requests.post(f"{self.api_url}/activate", json={"machine_id": machine_id, "license_key": license_key})
            if response.status_code == 200:
                data = response.json()
                return data.get("success"), data.get("message")
            return False, "Server Error"
        except Exception as e:
            return False, "Connection Failed"