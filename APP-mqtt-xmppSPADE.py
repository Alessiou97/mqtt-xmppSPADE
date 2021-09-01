import time
from random import choice
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json
import requests
import paho.mqtt.client as mqtt
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read('simple.ini')
URL_1 = parser.get('bug_tracker', 'URL_1')
URL_2 = parser.get('bug_tracker', 'URL_2')

class SenderAgent(Agent):
    class InformBehav(OneShotBehaviour):
        def __init__(self,string):
            super().__init__(   )
            self.string=""
            self.string=string
        async def run(self):
            print("InformBehav running")
            msg = Message(to="mary@jabber.hot-chilli.net")     # Instantiate the message
            msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
            msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
            msg.set_metadata("language", "OWL-S")       # Set the language of the message content
            msg.body = self.string               # Set the message content

            await self.send(msg)
            print("Message sent!")

            # set exit_code for the behaviour
            #self.exit_code = "Job Finished!"

            # stop agent from behaviour
            #await self.agent.stop()

    async def setup(self):
        print("SenderAgent started")
        #string="ciao"
        #self.b = self.InformBehav(string)
        #self.add_behaviour(self.b)
        

class Mymqtt:
    def __init__(self,agent,clientid=None):
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.on_message
        self._mqttc.on_connect = self.on_connect
        self.agent=agent
        
    def run(self):
        self._mqttc.connect("localhost",1883)
        rc=0
        while rc==0:
            rc=self._mqttc.loop()
        return rc
       
        
    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("hermes/intent/#")
        client.subscribe("hermes/nlu/intentNotRecognized")
        print("Connected. Waiting for intents.")
        print(self.agent.is_alive())
    
    def on_message(self,client, userdata, msg):
        """Called each time a message is received on a subscribed topic."""
        print(agent.is_alive())
        nlu_payload = json.loads(msg.payload)
        site_id = nlu_payload["siteId"]
         
        if msg.topic == "hermes/nlu/intentNotRecognized":
           # sentence = "Unrecognized command!"
           #sentence = nlu_payload["input"]
           ex = ('chi sono', 'parlare dell arco di capua', ' del ultimo restauro')
           ex2 = choice(ex)
           client.publish("hermes/tts/say", json.dumps({"text": "Non riesco a capire. Puoi chiedermi"+ex2, "siteId": site_id}))
           print("Recognition failure")
           print(nlu_payload)
       
        else:
            # Intent
            #client.publish("hermes/tts/say", json.dumps({"text": "Attendi una risposta", "siteId": site_id}))
            print("Got intent:", nlu_payload["intent"]["intentName"])

            # Speak the text from the intent
            sentence = nlu_payload["input"]
 
            payload = {"sender": "salvatore", "message": sentence}
            r = requests.post(URL_1, data=json.dumps(payload))
        
            data = json.loads(r.text)
            r1 = requests.post(URL_2, data=json.dumps(payload))
            data1 = json.loads(r1.text)
            string2 = json.dumps(data1["tracker"]["latest_message"]["intent"]["name"],ensure_ascii=False)
        
            new_string2=string2.replace('"','')
            #future = agent.start()
            #future.result()
            self.b = agent.InformBehav(new_string2)
            agent.add_behaviour(self.b)
            for i in data:
                time.sleep(5)
                string=""
                print(i["text"])
                string= json.dumps(i["text"],ensure_ascii=False)
                new_string=string.replace('"','')
                #future = agent.start()
                #future.result()
                self.b1 = agent.InformBehav(new_string)
                agent.add_behaviour(self.b1)
        
            
if __name__ == "__main__":
    agent = SenderAgent("umbertoalessio@jabber.hot-chilli.net", "password")
    future = agent.start()
    future.result()
    mqttc = Mymqtt(agent)
    rc = mqttc.run()
