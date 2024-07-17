import requests
from datetime import datetime

class CanadaPostTracker:
    def __init__(self, tracking_id):
        self.tracking_id = tracking_id
        self.shipping_url = f"https://www.canadapost-postescanada.ca/track-reperage/rs/track/json/package?pins={tracking_id}"

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