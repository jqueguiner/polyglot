import os
import sys
import requests
import yaml
import json
from googletrans import Translator



class Monitoring(object):

    def __init__(self, config_path, experiment_name):
        self.translator = Translator()
        self.experiment_name = experiment_name
        self.get_config(config_path)
        self.start_experiment()
        
        


    def get_config(self, config_path):

        try:
            with open(config_path, 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
                self.api_url = "%s:%s" % (self.cfg['monitoring-api']['url'], self.cfg['monitoring-api']['port'])
                self.api_write_token = self.cfg['monitoring-api']['write_token']
                self.headers = {'X-API-TOKEN': self.api_write_token}
                print(self.api_url)
        except:
            sys.exc_info()
            print("""
                Missing %s file.
                Please create it before running this script.""" % "~/.gpt_2_simple/config.yml")
            print("""

                File content should look like this:


                monitoring-api:
                    url: http://localhost
                    port: 6006
                    write_token: 'NH4NRq3RZcDfyYVM7BupnDpseoBEXkiuRrqeRk2QWXzgGua7VpfRHHRNNHn4AvgM'
            """)

            sys.exit(1)

    def get_experiment_by_name(self):
        payload = json.dumps({'name': "%s" % self.experiment_name})
        r = requests.get(url = '%s/get_experiment_by_name' % self.api_url, data=payload, headers=self.headers)
        return json.loads(r.text)

    def create_experiment(self, name, description):
        headers = {'X-API-TOKEN': self.api_write_token}
        payload = json.dumps({'name': "%s" % name, 'description': "%s" % description})
        r = requests.post(url = '%s/create_experiment' % self.api_url, data=payload, headers=self.headers)
        return json.loads(r.text)
        
    def start_experiment(self):
        self.experiment = self.get_experiment_by_name()
        print('[INFO] starting experiment : %s' % self.experiment_name)
        self.experiment_id = self.experiment['id']

        if self.experiment_id == 0:
            self.experiment_id = self.create_experiment(self.experiment_name, self.experiment_name)['id']
        
            

    def push_metric(self, key, value, step, t):
        
        payload = json.dumps({'key': key, 'value': float(value), 'step': step, 'experiment_id': self.experiment_id, 'time': float(t)})
        try:
            r = requests.post('%s/push_metric' % self.api_url, data=payload, headers=self.headers)
        except:
            print('[ERROR] Failed sending metrics')

    def push_text(self, key, value, step, loss, t):
        headers = {'X-API-TOKEN': self.api_write_token}
        text_en = ''
        try:
            text_en=translator.translate(value).text
        except:
            print("[ERROR] failed translating text")
        try:
            payload = json.dumps({
                'key': key, 
                'value': value,
                'text_en': text_en,
                'step': step, 
                'experiment_id': self.experiment_id, 
                'time': float(t), 
                'loss': float(loss)
                })
            r = requests.post('%s/push_text' % self.api_url, data=payload, headers=self.headers)
        except:
            print("failed sending text")
