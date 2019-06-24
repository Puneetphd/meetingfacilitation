# [START gae_python37_app]
from flask import Flask
from spade import agent


import spade


import asyncio
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
import time
from spade.message import Message
from spade.template import Template
import requests

import pickle as pic

from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import re
from urllib.request import urlopen
import cloudpickle as cp

from nltk.stem import PorterStemmer
from addattrs import *

from nltk.stem import PorterStemmer


app = Flask(__name__)
class FacilitatorAgent(agent.Agent):
    
    class setfinalPreference(OneShotBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
      
        async def run(self):
            print("Running Behaviour")
            pickle_in = open("/home/puneet/Downloads/onss.pkl","rb")
            print("pickle_in is populated")
            clf = pic.load(pickle_in)
            #clf = cp.load(urlopen("http://puneetphd.esy.es/api/MeetingFacilitation/pickle/modulesd.pkl"))
            print("Pickle is loaded finally")    
            resp = requests.get('http://puneetphd.esy.es/api/MeetingFacilitation/selectunfinalised.php')
            #carve out the twits array from response
            opinions=[]
            results=[]
            if not resp.json() == 'nothing':
                print("total Records are")
                print(resp.json())
                for x in resp.json():
                    opinions.append(x['a1view'])   
                    opinions.append(x['a2view'])
                    opinions.append(x['a3view'])

                preds = clf.predict(opinions)
                k=0
            
                for j in resp.json():
                    if(int(preds[k])==1):
                        j['a1pospolarity']=1
                    else:
                        j['a1negpolarity']=1
                    if(int(preds[k+1])==1):
                        j['a2pospolarity']=1
                    else:
                        j['a2negpolarity']=1
                    if(int(preds[k+2])==1):
                        j['a3pospolarity']=1
                    else:
                        j['a3negpolarity']=1
                    #Earlier in prediction for empty string polarity is counted 1 thus need to be changed
                    k=k+3
                    if j['a1view']=="":
                        j['a1negpolarity']=0
                        j['a1pospolarity']=0
                        j['a1noview']=1
                    if j['a2view']=="":
                        j['a2negpolarity']=0
                        j['a2pospolarity']=0
                        j['a2noview']=1
                    if j['a3view']=="":
                        j['a3negpolarity']=0
                        j['a3pospolarity']=0
                        j['a3noview']=1
                    print("Recod processed is :")
                    print((k/3))
                    #For testing
                    resp1 = requests.post('http://puneetphd.esy.es/api/MeetingFacilitation/updatepolarities.php', json=j)
                    #print(resp1.json())
                print("Internal Loop is finished")
                resp2 = requests.get('http://puneetphd.esy.es/api/MeetingFacilitation/FinalisedTotalPolarities.php')    
            else:
                print("Nothing happened")  
            self.agent.stop()
                

    def setup(self):
        print("Hello World! I'm Facilitator  agent {}".format(str(self.jid)))
        
        b = self.setfinalPreference()
        self.add_behaviour(b)
        

@app.route('/')
def hello():
    
    """Return a friendly HTTP greeting."""
    return 'Hello from facilitator AGENT!'


@app.route('/fac')
def facilitate():
    print("Agent is going to start")
    fa = FacilitatorAgent("punmod@jabber.ru", "hareram&1")
    fa.start()
   
    
    while  fa.is_alive():
        try:
           
            time.sleep(1)
        except KeyboardInterrupt:
            break
    fa.stop()
    return 'I think it is happening'

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    
    
    app.run(host='0.0.0.0', port=8080, debug=False)
    # [END gae_python37_app]
