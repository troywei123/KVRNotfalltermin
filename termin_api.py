import json
import re
import requests
import ddddocr
import time
import random
import sys, os

class KVR():

    @staticmethod
    def get_frame_url():
        return 'https://terminvereinbarung.muenchen.de/abh/termin/'
    
    @staticmethod
    def get_capchaimg_url():
        return 'https://terminvereinbarung.muenchen.de/abh/securimage/securimage_show.php'


def get_termins(buro):

    # Session is required to keep cookies between requests
    s = requests.Session()
    
    # First request to get and save cookies
    
    first_page = s.get(buro.get_frame_url())
    try:
        token = re.search('FRM_CASETYPES_token" value="(.*?)"', first_page.text).group(1)
    except AttributeError:
        token = None
    # print(token)

    
    #image OCR
    captcha_response = s.get(buro.get_capchaimg_url(), verify=False)
    # print(captcha_response.text)
    with open ('verify.png', mode= 'wb') as f:
        f.write(captcha_response.content)
        

    
    with open('verify.png', mode='rb') as f:
        img=f.read()
        
    # sys.stdout =open(os.devnull,'w')    
    ocr=ddddocr.DdddOcr()    

    # sys.stdout =sys.__stdout__
    code=ocr.classification(img)
    #manual input
    # code=input('input captcha：')
    # print(code)
    
    termin_data = {
        'CASETYPES[Notfalltermin UA 35]': 1,
        'step': 'WEB_APPOINT_SEARCH_BY_CASETYPES',
        'FRM_CASETYPES_token': token,
        'captcha_code': code
    }

    response = s.post(buro.get_frame_url(), termin_data)
    txt = response.text

    json_str = re.search('jsonAppoints = \'(.*?)\'', txt).group(1)
  
    appointments = json.loads(json_str)

    return appointments


if __name__ == '__main__':

    # search for Termin, gap 10-20 second
    while True:
        
        #try captcha, gap 2-5 second
        while True:
            try:  
                appointment_data = get_termins(KVR)
            except AttributeError:
                print('one failure to identify the captcha, another try')
                time.sleep(random.randint(2,5))
                continue
            break
        
        availiable=False
        appointments = appointment_data['LOADBALANCER']['appoints']
        # print(appointments)
        
        for day in appointments:
            if len(appointments[day]):
                print('yes!')
                availiable=True
                break
                
        print('No termin, continue refresh in 10-20 second')     
        
        time.sleep(random.randint(10,20))        

