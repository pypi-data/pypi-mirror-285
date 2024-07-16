import requests
import time
import json
from datetime import datetime

class CanadaPostTracker:
    def __init__(self, tracking_id, delay=1):
        self.tracking_id = tracking_id
        self.shipping_url = f"https://www.canadapost-postescanada.ca/track-reperage/rs/track/json/package?pins={tracking_id}"
        self.delay = delay
        self.last_status = None

    def check_shipping(self):
        try:
            response = requests.get(url=self.shipping_url)
            if response.status_code == 200:
                data = response.json()
                addtnl_orig_info = data[0].get('addtnlOrigInfo', 'N/A')
                addtnl_dest_info = data[0].get('addtnlDestInfo', 'N/A')
                status = data[0].get('status', 'N/A')
                perrmstat = data[0].get('status', 'N/A')
                expected_delivery = data[0].get('expectedDlvryDateTime', {}).get('dlvryDate', 'N/A')
                if expected_delivery != 'N/A':
                    expected_delivery_date = datetime.strptime(expected_delivery, '%Y-%m-%d')
                    formatted_delivery_date = expected_delivery_date.strftime('%A, %B %d, %Y')
                else:
                    formatted_delivery_date = 'N/A'

                if status == "FullAccepted":
                    status = "ITEM PICKED UP BY CARRIER"
                else:
                    status = status    

                if status != self.last_status:
                    self.last_status = status
                    return {
                        "Sent From": addtnl_orig_info,
                        "Shipping To": addtnl_dest_info,
                        "Status": status,
                        "Expected Delivery Date": formatted_delivery_date,
                        "Tracking Number": self.tracking_id,
                        "Status Detail": perrmstat
                    }
            else:
                print("Check the shipping number and try again")    
        except Exception as e:
            print(f'Error: {e}')
        return None

    def start_tracking(self):
        while True:
            shipping_info = self.check_shipping()
            if shipping_info:
                print(shipping_info)
            time.sleep(self.delay * 60)