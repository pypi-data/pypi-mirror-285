import requests
from datetime import datetime
"""
monetize

A python library to make some money
"""

__VERSION__ = "1.0.0"
__AUTHOR__ = 'Dylan Lang'
__CREDITS__ = 'Dylan Lang'



class monetize:
    key = ''
    headers = ''
    
    def __init__(self,key,debug = False):
        self.key = key
        self.headers = {'Authorization':'Bearer {}'.format(key)}
        self.debug = debug
        return
    
    def accrue(self,amount,subscription_item_id):
        if subscription_item_id == None:
            return False
        else:
            url = 'https://api.stripe.com/v1/subscription_items/{}/usage_records'.format(subscription_item_id)
            data = {
                "quantity":amount,
                "timestamp":int(datetime.timestamp(datetime.now()))
            }
            try:
                response = requests.post(url,headers=self.headers,data=data).json()
                if response['subscription_item'] == subscription_item_id:
                    if self.debug == True:
                        return response
                    else:
                        return True
                else:
                    if self.debug == True:
                        return response
                    else:
                        return False
            except:
                if self.debug == True:
                    return response
                else:
                    return False