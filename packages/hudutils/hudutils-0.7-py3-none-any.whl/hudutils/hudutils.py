# hudutils/hudutils.py

import json
import time, sys, os

def flatten_json(json_data, parent_key='', sep='.'):
    items = []
    for k, v in json_data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                items.extend(flatten_json({f"{new_key}[{i}]": item}, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)



def filename_with_rollover(file_path='hud.log', opts = ['year','month','day']):
    
    file_path = os.path.join(file_path)
    file_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)
    

    """
    
    HELP:
    filename     = text.txt
    new_filename = filename_with_rollover(filename, opts = ['year','month','day'])
    
    
    """

    allowed = ['year','month','day','hour','mins','sec']
    name    = ''
    schema  = ''
    localtime = time.localtime(time.time())
    timer   = {}

    timer['year']  = str(localtime.tm_year)
    timer['month'] = str(localtime.tm_mon)
    timer['day']   = str(localtime.tm_mday)
    timer['hour']  = str(localtime.tm_hour)
    timer['mins']  = str(localtime.tm_min)
    timer['sec']   = str(localtime.tm_sec)

    for n in opts:
        if n not in allowed:
            print ("""
            
            The filename_with_rollover function must contain 
            one of the following:
            ['year','month','day','hour','mins','sec']
            
            """)
            sys.exit()
        else:
            name   = name+timer[n]
            schema = schema+n+'_'        
    filen_ = name + '_' + file_name
    
    new_file_path = os.path.join(dir_name, filen_)
    
    return new_file_path



#############
#############


class ElasticsearchDataFetcher:

    def __init__(self, config_file):
        self.config = self.load_config(config_file)

    def load_config(self, config_file):
        try:
            with open(os.path.join(config_file), 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error("Configuration file not found.")
            return None
        except json.JSONDecodeError:
            logging.error("Invalid JSON in configuration file.")
            return None

    def fetch_data(self, index_, query_string=None):
        if not self.config:
            return []

        # Read the last sequence number from file
        try:
            with open(os.path.join(self.config['sequence_file']), 'r') as file:
                last_sequence_num = int(file.read().strip())
        except FileNotFoundError:
            logging.info("Sequence file not found. Starting from the beginning.")
            last_sequence_num = 0
        except ValueError:
            logging.error("Invalid data in sequence file.")
            return []

        # Elasticsearch query
        query = {
            "query": {
                "bool": {
                    "must": {
                        "range": {
                            "sequence_num": {
                                "gt": last_sequence_num
                            }
                        }
                    }
                }
            },
            "sort": [
                {"sequence_num": "asc"}
            ],
            "size": self.config['batch_size'],
            "_source": ["title", "@timestamp", "link_content", "link", "data_source", "sequence_num", "description", "fingerprint"]
        }

        # Add the query_string to the query if provided
        if query_string:
            query['query']['bool']['filter'] = {
                "query_string": {
                    "query": query_string
                }
            }

        try:
            response = requests.get(f"{self.config['base_url']}/{index_}/_search", 
                                    auth=tuple(self.config['auth']),
                                    headers={'Content-Type': 'application/json'}, 
                                    data=json.dumps(query),
                                    verify=False,
                                    timeout=10)
            response.raise_for_status()
        except RequestException as e:
            logging.error(f"Error making request to Elasticsearch: {e}")
            return []

        # Extract data from response
        data = response.json().get('hits', {}).get('hits', [])

        # Update the last sequence number
        if data:
            try:
                last_sequence_num = data[-1]['_source']['sequence_num']
                with open(os.path.join(self.config['sequence_file']), 'w') as file:
                    file.write(str(last_sequence_num))
            except KeyError:
                logging.error("Error updating the last sequence number.")
                return []

        return data

    def run_query(self, index_, query_string, size=10000):
        if not self.config:
            return []
        
        query = {
            "query": {
                "query_string": {
                    "query": query_string
                }
            },
            "size": size,
        }
    
        headers = {
            'Content-Type': 'application/json'
        }
    
        try:
            response = requests.get(f"{self.config['base_url']}/{index_}/_search", 
                                    auth=tuple(self.config['auth']),
                                    headers={'Content-Type': 'application/json'}, 
                                    data=json.dumps(query),
                                    verify=False,
                                    timeout=10)
            return response.json().get('hits', {}).get('hits', [])
        except (HTTPError, ConnectionError, Timeout) as e:
            logging.error(f"Network error: {e}")
            return f"Network error: {e}"
        except RequestException as e:
            logging.error(f"Request error: {e}")
            return f"Request error: {e}"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"

    def send_to_elasticsearch(self, docs, indext, attempt=1, max_attempts=5):
        es_url = f"{self.config['base_url']}/{indext}/_bulk"
        headers = {'Content-Type': 'application/x-ndjson'}

        # Prepare data for bulk API
        data = '\n'.join(json.dumps({'index': {}}) + '\n' + json.dumps(doc) for doc in docs) + '\n'

        try:
            response = requests.post(es_url, headers=headers, data=data, auth=tuple(self.config['auth']), verify=False, timeout=10)
            response.raise_for_status()  # This will raise an exception for HTTP error codes
            if response.json().get('errors', False):
                logging.error("Bulk index operation had errors")
            else:
                print("Documents indexed successfully.")
        except RequestException as e:
            if attempt <= max_attempts:
                logging.error(f"Attempt {attempt} failed with error: {e}. Retrying after delay...")
                sleep(attempt * 2)  # Exponential back-off
                self.send_to_elasticsearch(docs, indext, attempt + 1, max_attempts)
            else:
                logging.error(f"Failed to index documents after {max_attempts} attempts.")
