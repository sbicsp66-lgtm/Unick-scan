import win32com.client
import os

class ScannerEngine:
    def __init__(self):
        try:
            self.device_manager = win32com.client.Dispatch("WIA.DeviceManager")
        except Exception as e:
            print("WIA Driver Error:", e)

    def get_scanners(self):
        scanners = []
        try:
            # Type 1 mane Scanner Device
            for info in self.device_manager.DeviceInfos:
                if info.Type == 1: 
                    scanners.append(info.Properties("Name").Value)
        except Exception:
            pass
        return scanners

    def scan_document(self, save_path="temp_scan.jpg"):
        try:
            # WIA dialog box open korbe scan korar jonno
            common_dialog = win32com.client.Dispatch("WIA.CommonDialog")
            image = common_dialog.ShowAcquireImage()
            
            if image:
                if os.path.exists(save_path):
                    os.remove(save_path)
                image.SaveFile(save_path)
                return True, save_path
            return False, "Scan cancelled by user."
        except Exception as e:
            return False, f"Scan Error: {str(e)}"