import subprocess
import requests

class LicenseManager:
    def __init__(self):
        # আপনার Railway Live Link
        self.api_url = "https://unick-scan-production.up.railway.app/api"

    def get_machine_id(self):
        try:
            output = subprocess.check_output('wmic csproduct get uuid', shell=True)
            return output.decode().split('\n')[1].strip()
        except:
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
                    days_left = data.get("days_left", 0)
                    return True, days_left
        except Exception as e:
            print("Connection error:", e)
        return False, "Expired"

    def activate_license(self, key):
        machine_id = self.get_machine_id()
        try:
            response = requests.post(f"{self.api_url}/activate", json={"machine_id": machine_id, "license_key": key})
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return True, data.get("message")
                return False, data.get("message")
        except Exception as e:
            return False, f"Connection error: {e}"
        return False, "Failed to connect to server."
