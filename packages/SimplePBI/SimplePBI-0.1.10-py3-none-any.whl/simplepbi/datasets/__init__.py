'''.
           @@@@@@@@@@
       @@@@..........@@@@
    @@@         .        @@@
  @@.           .         . @@
 @  .     _     .         .   @
@........| |...................@    *********************************************
@      . | |   _____  .        @
@      . | |  |  __ \ .        @    La Data Web
@      . | |__| |  | |.   ***  @
@........|____| |  | |...*   *.@    Copyright © 2022 Ignacio Barrau
@   .       . | |__| |. *     *@
@   .       . |_____/ . *     *@    *********************************************
@   .       .         . *     *@
@   .       .         . *******@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
'''

import json
import requests
from simplepbi import utils
import pandas as pd

class Datasets():
    """Simple library to use the Power BI api and obtain datasets from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request admin API
        Args:
            token: String
                Bearer Token to use the Power Bi Rest API
        """
        self.token = token
    
    def get_dataset(self, dataset_id):
        """Returns the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a dataset in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataset_in_group(self, workspace_id, dataset_id):
        """Returns the specified dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a dataset in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_datasets(self):
        """Returns a list of datasets from My workspace.
        ### Parameters
        ----
        None
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasets in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets"
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_datasets_in_group(self, workspace_id):
        """Returns a list of datasets from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasets in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def get_datasources(self, dataset_id):
        """Returns a list of data sources for the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasources in the dataset from My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/datasources".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_datasources_in_group(self, workspace_id, dataset_id):
        """Returns a list of data sources for the specified dataset from the specified workspace
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the datasources in the dataset from the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/datasources".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_dataset_to_dataflows_links_in_group(self, workspace_id):
        """Returns a list of upstream dataflows for datasets from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all upstream dataflows in the dataset from a workspace
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/upstreamDataflows".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            if res.text == '':
                res.raise_for_status()
                return res
            else:
                res.raise_for_status()
                return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)

    def get_direct_query_refresh_schedule(self, dataset_id):
        """Returns the refresh schedule for a specified DirectQuery or LiveConnection dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing the direct query refresh schedule in a dataset from My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/directQueryRefreshSchedule".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_direct_query_refresh_schedule_in_group(self, workspace_id, dataset_id):
        """Returns the refresh schedule for a specified DirectQuery or LiveConnection dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing the direct query refresh schedule in a dataset from a workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/directQueryRefreshSchedule".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_gateway_datasources(self, dataset_id):
        """This API is deprecated, use Get Datasources instead.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        """
        print("This API is deprecated, use Get Datasources instead.")
    def get_gateway_datasources_in_group(self, dataset_id):
        """This API is deprecated, use Get Datasources In Group instead.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        """
        print("This API is deprecated, use Get Datasources In Group instead.")
        
    def get_parameters(self, dataset_id):
        """Returns a list of parameters for the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the parameters in the dataset from My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/parameters".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_parameters_in_group(self, workspace_id, dataset_id):
        """Returns a list of parameters for the specified dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the parameters in the dataset from workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/parameters".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
    
    def get_refresh_history(self, dataset_id, top=None):
        """Returns the refresh history for the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        top: int
            The requested number of entries in the refresh history. If not provided, the default is all available entries.
        ### Returns
        ----
        Dict:
            A dictionary containing a refresh history in a dataset in My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/refreshes".format(dataset_id)
            if top != None:
                url = url + "?$top={}".format(str(top))
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_refresh_history_in_group(self, workspace_id, dataset_id, top=None):
        """Returns the refresh history for the specified dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        top: int
            The requested number of entries in the refresh history. If not provided, the default is all available entries.
        ### Returns
        ----
        Dict:
            A dictionary containing a refresh history in a dataset from workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshes".format(workspace_id, dataset_id)
            if top != None:
                url = url + "?$top={}".format(str(top))
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_refresh_schedule(self, dataset_id):
        """Returns the refresh schedule for the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a refresh schedule in a dataset from My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/refreshSchedule".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_refresh_schedule_in_group(self, workspace_id, dataset_id):
        """Returns the refresh schedule for the specified dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a refresh schedule in a dataset from workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshSchedule".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def refresh_dataset(self, dataset_id, notifyOption):
        """Triggers a refresh for the specified dataset from My workspace.
        For Shared capacities, a maximum of eight requests per day, which includes refreshes executed using a scheduled refresh.
        ### Parameters
        ----    
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        notifyOption: NotifyOption str
            Mail notification options (success and/or failure, or none). Options: { MailOnCompletion, MailOnFailure, NoNotification }
        ### Returns
        ----
        Response object from requests library. 202 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/refreshes".format(dataset_id)
            body = {
                "notifyOption": notifyOption 
            }                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def refresh_dataset_in_group(self, workspace_id, dataset_id, notifyOption):
        """Triggers a refresh for the specified dataset from the specified workspace.
        For Shared capacities, a maximum of eight requests per day, which includes refreshes executed using a scheduled refresh.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        notifyOption: NotifyOption str
            Mail notification options (success and/or failure, or none). Options: { MailOnCompletion, MailOnFailure, NoNotification }
        ### Returns
        ----
        Response object from requests library. 202 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshes".format(workspace_id, dataset_id)
            body = {
                "notifyOption": notifyOption 
            }               
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def take_over_dataset_in_group(self, workspace_id, dataset_id):
        """Transfers ownership over the specified dataset to the current authorized user.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        None
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/Default.TakeOver".format(workspace_id, dataset_id)
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def discover_gateways(self, dataset_id):
        """Returns a list of gateways that the specified dataset from My workspace can be bound to.
        This API call is only relevant to datasets that have at least one on-premises connection. For datasets with cloud-only connections, this API call returns an empty list.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a list of gateways from My workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/Default.DiscoverGateways".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def discover_gateways_in_group(self, workspace_id, dataset_id):
        """Returns a list of gateways that the specified dataset from the specified workspace can be bound to.
        This API call is only relevant to datasets that have at least one on-premises connection. For datasets with cloud-only connections, this API call returns an empty list.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id:
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a list of gateways from the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/Default.DiscoverGateways".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def delete_dataset(self, dataset_id):
        """Deletes the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}".format(dataset_id)   
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.delete(url, headers=headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def delete_dataset_in_group(self, workspace_id, dataset_id):
        """Deletes the specified dataset from the specified workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id)   
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.delete(url, headers=headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def execute_queries(self, dataset_id, query, return_pandas=False):
        """Executes Data Analysis Expressions (DAX) queries against the provided dataset. The dataset must reside in My workspace or another new workspace experience workspace.
        DAX query errors will result in: A response error, such as DAX query failure. A failure HTTP status code (400).
        Limitation: A query that requests more than one table, or more than 100,000 table rows, will result in Error.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        query: str
            DAX query returning a Table. Starts with EVALUATE
        return_pandas: bool
            Flag to specify if you want to return a dict response or a pandas dataframe of events.
        ### Returns
        ----
        If return_pandas = True returns a Pandas dataframe concatenating iterations otherwise it returns a dict of the response
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/executeQueries".format(dataset_id)
            body = {"queries": [{"query": query}], "serializerSettings": {"includeNulls": "true"}}
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = json.dumps(body), headers = headers)      
            #Encode text in json to avoid Unexpected UTF-8 BOM (decode using utf-8-sig)
            encoded_data = json.loads(res.text.encode().decode('utf-8-sig'))
            if return_pandas:
                #get columns from json response - keys from dict
                tabla_columnas = list(encoded_data['results'][0]['tables'][0]['rows'][0].keys())
                columnas = [columnita.split("[")[1].split("]")[0] for columnita in tabla_columnas]
                print(columnas)
                #get the number of rows to loop data
                rows = len(encoded_data['results'][0]['tables'][0]['rows'])        
                print(rows)
                #get data from json response - values from dict
                datos = [list(encoded_data['results'][0]['tables'][0]['rows'][n].values()) for n in range(rows-1)]
                print("datos")
                #build a dataframe from the collected data
                df = pd.DataFrame(data=datos, columns=columnas)
                print(df.head())
                return df
            else:
                return encoded_data
        except requests.exceptions.HTTPError as ex:
            print("ERROR ", ex)
        except Exception as e:
            print("ERROR ", e)
            
    def execute_queries_in_group(self, workspace_id, dataset_id, query, return_pandas=False, impersonatedUserName=None):
        """Executes Data Analysis Expressions (DAX) queries against the provided dataset. The dataset must reside in My workspace or another new workspace experience workspace.
        DAX query errors will result in: A response error, such as DAX query failure. A failure HTTP status code (400).
        Limitation: A query that requests more than one table, or more than 100,000 table rows, will result in Error.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL    
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        return_pandas: bool
            Flag to specify if you want to return a dict response or a pandas dataframe of events.
        ### Body
        ----
        query: str
            Requested. DAX query returning a Table. Starts with EVALUATE
        impersonatedUserName: str
            The UPN of a user to be impersonated. If the model is not RLS enabled, this will be ignored. E.g. "someuser@mycompany.com"
        ### Returns
        ----
        If return_pandas = True returns a Pandas dataframe concatenating iterations otherwise it returns a dict of the response
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/executeQueries".format(workspace_id, dataset_id)
            body = {"queries": [{"query": query}], "serializerSettings": {"includeNulls": "true"}}
            if impersonatedUserName != None:
                body["impersonatedUserName"]=impersonatedUserName
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = json.dumps(body), headers = headers)      
            res.raise_for_status()
            #Encode text in json to avoid Unexpected UTF-8 BOM (decode using utf-8-sig)
            encoded_data = json.loads(res.text.encode().decode('utf-8-sig'))
            if return_pandas:
                #get columns from json response - keys from dict
                tabla_columnas = list(encoded_data['results'][0]['tables'][0]['rows'][0].keys())
                columnas = [columnita.split("[")[1].split("]")[0] for columnita in tabla_columnas]
                print(columnas)
                #get the number of rows to loop data
                rows = len(encoded_data['results'][0]['tables'][0]['rows'])        
                print(rows)
                #get data from json response - values from dict
                datos = [list(encoded_data['results'][0]['tables'][0]['rows'][n].values()) for n in range(rows-1)]
                print("datos")
                #build a dataframe from the collected data
                df = pd.DataFrame(data=datos, columns=columnas)
                print(df.head())
                return df
            else:
                return encoded_data
        except requests.exceptions.HTTPError as ex:
            print("ERROR ", ex)
        except Exception as e:
            print("ERROR ", e)
            
    def update_parameters(self, dataset_id, updateDetails):
        """Updates the parameters values for the specified dataset from My workspace.
        If you're using enhanced dataset metadata, refresh the dataset to apply the new parameter values.
        If you're not using enhanced dataset metadata, wait 30 minutes for the update data sources operation to complete, and then refresh the dataset.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        updateDetails: UpdateMashupParameterDetails [] str
            The dataset parameter list to update. Example:
            [
                {
                    "name": "ParameterName1",
                    "newValue": "NewDB"
                },
                {
                    "name": "ParameterName2",
                    "newValue": "5678"
                }
            ]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        Datasets created using the public XMLA endpoint aren't supported. To make changes to those data sources, the admin must use the Azure Analysis Services client library for Tabular Object Model.
        DirectQuery connections are only supported with enhanced dataset metadata.
        Datasets with Azure Analysis Services live connections aren't supported.
        Maximum of 100 parameters per request.
        All specified parameters must exist in the dataset.
        Parameters values should be of the expected type.
        The parameter list cannot be empty or include duplicate parameters.
        Parameters names are case-sensitive.
        Parameter IsRequired must have a non-empty value.
        The parameter types Any and Binary cannot be updated.
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/Default.UpdateParameters".format(dataset_id)
            body = {
                "updateDetails": updateDetails
            }               
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_parameters_in_group(self, workspace_id, dataset_id, updateDetails):
        """Updates the parameters values for the specified dataset from the specified workspace.
        If you're using enhanced dataset metadata, refresh the dataset to apply the new parameter values.
        If you're not using enhanced dataset metadata, wait 30 minutes for the update data sources operation to complete, and then refresh the dataset.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        updateDetails: UpdateMashupParameterDetails [] str
            The dataset parameter list to update. Example:
            [
                {
                    "name": "ParameterName1",
                    "newValue": "NewDB"
                },
                {
                    "name": "ParameterName2",
                    "newValue": "5678"
                }
            ]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        Datasets created using the public XMLA endpoint aren't supported. To make changes to those data sources, the admin must use the Azure Analysis Services client library for Tabular Object Model.
        DirectQuery connections are only supported with enhanced dataset metadata.
        Datasets with Azure Analysis Services live connections aren't supported.
        Maximum of 100 parameters per request.
        All specified parameters must exist in the dataset.
        Parameters values should be of the expected type.
        The parameter list cannot be empty or include duplicate parameters.
        Parameters names are case-sensitive.
        Parameter IsRequired must have a non-empty value.
        The parameter types Any and Binary cannot be updated.
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/Default.UpdateParameters".format(workspace_id, dataset_id)
            body = {
                "updateDetails": updateDetails
            }               
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_refresh_schedule(self, dataset_id, NotifyOption=None, days=None, enabled=None, localTimeZoneId=None, times=None):
        """Updates the refresh schedule for the specified dataset from My workspace.
        A request that disables the refresh schedule should contain no other changes.
        At least one day must be specified. If no times are specified, then Power BI will use a default single time per day.        
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        NotifyOption: ScheduleNotifyOption str
            Notification option at scheduled refresh termination. Example MailOnFailure or NoNotification.
        days: str []
            Days to execute the refresh. Example: ["Sunday", "Tuesday"]
        enabled: bool
            is the refresh enabled
        localTimeZoneId: str
            The ID of the timezone to use. See TimeZone Info. Example "UTC"
        times: str []
            Times to execute the refresh within each day. Example: ["07:00", "16:00"]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        The limit on the number of time slots per day depends on whether a Premium or Shared capacity is used.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/refreshSchedule".format(dataset_id)
            body = {
                "value": {}
            }
            
            if NotifyOption != None:
                body["value"]["NotifyOption"]=NotifyOption
            if days != None:
                body["value"]["days"] = days
            if enabled != None:
                body["value"]["enabled"] = enabled
            if localTimeZoneId != None:
                body["value"]["localTimeZoneId"] = localTimeZoneId
            if times != None:
                body["value"]["times"]=times
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.patch(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_refresh_schedule_in_group(self, workspace_id, dataset_id, NotifyOption=None, days=None, enabled=None, localTimeZoneId=None, times=None):
        """Updates the refresh schedule for the specified dataset from the specified workspace.
        A request that disables the refresh schedule should contain no other changes.
        At least one day must be specified. If no times are specified, then Power BI will use a default single time per day.       
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        NotifyOption: ScheduleNotifyOption str
            Notification option at scheduled refresh termination. Example MailOnFailure or NoNotification.
        days: str []
            Days to execute the refresh. Example: ["Sunday", "Tuesday"]
        enabled: bool
            is the refresh enabled
        localTimeZoneId: str
            The ID of the timezone to use. See TimeZone Info. Example "UTC"
        times: str []
            Times to execute the refresh within each day. Example: ["07:00", "16:00"]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        The limit on the number of time slots per day depends on whether a Premium or Shared capacity is used.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshSchedule".format(workspace_id, dataset_id)
            body = {
                "value": {}
            }
            
            if NotifyOption != None:
                body["value"]["NotifyOption"]=NotifyOption
            if days != None:
                body["value"]["days"] = days
            if enabled != None:
                body["value"]["enabled"] = enabled
            if localTimeZoneId != None:
                body["value"]["localTimeZoneId"] = localTimeZoneId
            if times != None:
                body["value"]["times"]=times
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.patch(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def bind_to_gateway_preview(self, dataset_id, gatewayObjectId, datasourceObjectIds):
        """Binds the specified dataset from My workspace to the specified gateway, optionally with a given set of data source IDs. If you don’t supply a specific data source ID, the dataset will be bound to the first matching data source in the gateway. Only supports the on-premises data gateway
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        gatewayObjectId: str uuid
            The gateway ID. When using a gateway cluster, the gateway ID refers to the primary (first) gateway in the cluster and is similar to the gateway cluster ID.
        datasourceObjectIds: str []
            The unique identifier for the datasource in the gateway
        ### Returns
        ----
        Response object from requests library. 200 OK
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/Default.BindToGateway".format(dataset_id)
            body = {
                "gatewayObjectId": gatewayObjectId,
                "datasourceObjectIds": datasourceObjectIds
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def bind_to_gateway_in_group_preview(self, workspace_id, dataset_id, gatewayObjectId, datasourceObjectIds):
        """Binds the specified dataset from the specified workspace to the specified gateway, optionally with a given set of data source IDs. If you don’t supply a specific data source ID, the dataset will be bound to the first matching data source in the gateway. Only supports the on-premises data gateway
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        gatewayObjectId: str uuid
            The gateway ID. When using a gateway cluster, the gateway ID refers to the primary (first) gateway in the cluster and is similar to the gateway cluster ID.
        datasourceObjectIds: str []
            The unique identifier for the datasource in the gateway
        ### Returns
        ----
        Response object from requests library. 200 OK
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/Default.BindToGateway".format(workspace_id, dataset_id)
            body = {
                "gatewayObjectId": gatewayObjectId,
                "datasourceObjectIds": datasourceObjectIds
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_direct_query_refresh_schedule_in_group_preview(self, dataset_id, frequency=None, days=None, enabled=None, localTimeZoneId=None, times=None):
        """Updates the refresh schedule for a specified DirectQuery or LiveConnection dataset from My workspace.
        A request should contain either a set of days and times or a valid frequency, but not both. If you choose a set of days without specifying any times, then Power BI will use a default single time per day. Setting the frequency will automatically overwrite the days and times setting.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        frequency: int
            The interval in minutes between successive refreshes. Supported values are 15, 30, 60, 120, and 180.
        days: str []
            Days to execute the refresh. Example: ["Sunday", "Tuesday"]
        enabled: bool
            is the refresh enabled
        localTimeZoneId: str
            The ID of the timezone to use. See TimeZone Info. Example "UTC"
        times: str []
            Times to execute the refresh within each day. Example: ["07:00", "16:00"]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        The limit on the number of time slots per day depends on whether a Premium or Shared capacity is used.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/directQueryRefreshSchedule".format(dataset_id)
            body = {
                "value": {}
            }
            
            if frequency != None:
                body["value"]["frequency"]=frequency
            if days != None:
                body["value"]["days"] = days
            if enabled != None:
                body["value"]["enabled"] = enabled
            if localTimeZoneId != None:
                body["value"]["localTimeZoneId"] = localTimeZoneId
            if times != None:
                body["value"]["times"]=times
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.patch(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_direct_query_refresh_schedule_in_group_preview(self, workspace_id, dataset_id, frequency=None, days=None, enabled=None, localTimeZoneId=None, times=None):
        """Updates the refresh schedule for a specified DirectQuery or LiveConnection dataset from the specified workspace.
        A request should contain either a set of days and times or a valid frequency, but not both. If you choose a set of days without specifying any times, then Power BI will use a default single time per day. Setting the frequency will automatically overwrite the days and times setting.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        frequency: int
            The interval in minutes between successive refreshes. Supported values are 15, 30, 60, 120, and 180.
        days: str []
            Days to execute the refresh. Example: ["Sunday", "Tuesday"]
        enabled: bool
            is the refresh enabled
        localTimeZoneId: str
            The ID of the timezone to use. See TimeZone Info. Example "UTC"
        times: str []
            Times to execute the refresh within each day. Example: ["07:00", "16:00"]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        The limit on the number of time slots per day depends on whether a Premium or Shared capacity is used.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/directQueryRefreshSchedule".format(workspace_id, dataset_id)
            body = {
                "value": {}
            }
            
            if frequency != None:
                body["value"]["frequency"]=frequency
            if days != None:
                body["value"]["days"] = days
            if enabled != None:
                body["value"]["enabled"] = enabled
            if localTimeZoneId != None:
                body["value"]["localTimeZoneId"] = localTimeZoneId
            if times != None:
                body["value"]["times"]=times
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.patch(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_datasources_in_group_preview(self, workspace_id, dataset_id, updateDetails):
        """Updates the data sources of the specified dataset from the specified workspace.
        Only these data sources are supported: SQL Server, Azure SQL Server, Azure Analysis Services, Azure Synapse, OData, SharePoint, Teradata, and SAP HANA.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body (PLEASE READ THE DOCS)
        ----
        UpdateDetails[]: list
            A list of data source connection update requests. PLEASE READ THE DOCS
            E.g.[
                {
                  "datasourceSelector": {
                    "datasourceType": "Sql",
                    "connectionDetails": {
                      "server": "My-Sql-Server",
                      "database": "My-Sql-Database"
                    }
                  },
                  "connectionDetails": {
                    "server": "New-Sql-Server",
                    "database": "New-Sql-Database"
                  }
                }
            ]
        ### Returns
        ----
        Response object from requests library. 200 OK
        ### Limitations
        ----
        Datasets created using the public XMLA endpoint aren't supported.
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/Default.UpdateDatasources".format(workspace_id, dataset_id)
            body = {
                "updateDetails": updateDetails
            }
                
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            
            res = requests.post(url, json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)            
            
    def enhanced_refresh_dataset_in_group(self, workspace_id, dataset_id, objects, typeProcessing="Full", commitMode="transactional", maxParallelism=1, retryCount=1, applyRefreshPolicy=True):
        """Triggers a refresh for the specified dataset from the specified workspace.
        For Shared capacities, a maximum of eight requests per day, which includes refreshes executed using a scheduled refresh.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        ### Request Body
        ----
        typeProcessing: Enum (str)
            The type of processing to perform. Types are aligned with the TMSL refresh command types: full, clearValues, calculate, dataOnly, automatic, and defragment. Add type isn't supported.
        commitMode: Enum (str)
            Determines if objects will be committed in batches or only when complete. Modes include: transactional, partialBatch.
        maxParallelism: int
            Determines the maximum number of threads on which to run processing commands in parallel. This value aligned with the MaxParallelism property that can be set in the TMSL Sequence command or by using other methods.
        retryCount: int
            Number of times the operation will retry before failing.
        objects: array
            An array of objects to be processed. Each object includes table when processing the entire table, or table and partition when processing a partition. If no objects are specified, the entire dataset is refreshed.
            E.g. [ { "table": "DimCustomer", "partition": "DimCustomer" }  ,  { "table": "DimDate" } ]
        applyRefreshPolicy: boolean
            If an incremental refresh policy is defined, applyRefreshPolicy will determine if the policy is applied or not
        effectiveDate: date
            Comming Soon            
        ### Returns
        ----
        Response object from requests library. 202 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/refreshes".format(workspace_id, dataset_id)
            body = {
                "type": typeProcessing,
                "commitMode": commitMode,
                "maxParallelism": maxParallelism,
                "retryCount": retryCount,
                "objects": objects,
                "applyRefreshPolicy": applyRefreshPolicy
            }         
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_query_scaleout_sync_status(self, dataset_id):
        """Returns the query scale-out sync status for the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing data about scaleout sync dataset in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/datasets/{}/queryScaleOut/syncStatus".format(dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_query_scaleout_sync_status_in_group(self, workspace_id, dataset_id):
        """Returns the query scale-out sync status for the specified dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing data about scaleout sync dataset in the workspace.
        """
        try:
            url = "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/queryScaleOut/syncStatus".format(workspace_id, dataset_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def trigger_query_scaleout_sync(self, dataset_id):
        """Triggers a query scale-out sync of read-only replicas for the specified dataset from My workspace.
        ### Parameters
        ----
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        ### Returns
        ----
        Response object from requests library. 202 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/datasets/{}/queryScaleOut/sync".format(dataset_id)
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def trigger_query_scaleout_sync_in_group(self, workspace_id, dataset_id):
        """Triggers a query scale-out sync of read-only replicas for the specified dataset from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        ### Returns
        ----
        Response object from requests library. 202 OK
        
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}/queryScaleOut/sync".format(workspace_id, dataset_id)
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_dataset_in_group(self, workspace_id, dataset_id, targetStorageMode=None, autoSyncReadOnlyReplicas=None, maxReadOnlyReplicas=None):
        """Updates the properties for the specified dataset from the specified workspace. The user must be the dataset owner.
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL
        ### Request Body
        ----
        autoSyncReadOnlyReplicas: bool
            Whether the dataset automatically syncs read-only replicas
        maxReadOnlyReplicas: int
            Maximum number of read-only replicas for the dataset (0-64, -1 for automatic number of replicas)
        UpdateDatasetRequest: str
            Update dataset request
        ### Returns
        ----
        Response object from requests library. 200 OK
        """
        try: 
            url= "https://api.powerbi.com/v1.0/myorg/groups/{}/datasets/{}".format(workspace_id, dataset_id)
            body = {
                "queryScaleOutSettings":{}
            }
            
            if targetStorageMode != None:
                body["targetStorageMode"]=targetStorageMode
            if autoSyncReadOnlyReplicas != None:
                body["queryScaleOutSettings"]["autoSyncReadOnlyReplicas"]=autoSyncReadOnlyReplicas
            if maxReadOnlyReplicas != None:
                body["queryScaleOutSettings"]["maxReadOnlyReplicas"]=maxReadOnlyReplicas
            if targetStorageMode==None and autoSyncReadOnlyReplicas==None and maxReadOnlyReplicas==None:
                print("Error: You need to specify a parameter to modify.")                
            else:
                headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
                res = requests.patch(url, data = json.dumps(body), headers = headers)
                res.raise_for_status()
                return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_tables_from_dataset_in_group(self, workspace_id, dataset_id):
        """Get the tables from specific dataset in a workspace
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        ### Returns
        ----
        Response dict of tables from requests library. 200 OK
        """
        try:
            query = '''
            EVALUATE SELECTCOLUMNS( 
                		INFO.TABLES() 
                		, "ID", [ID]
                		, "Name", [Name]
                		, "IsHidden", [IsHidden]
                		, "ModifiedTime", [ModifiedTime]
                		, "StructureModifiedTime", [StructureModifiedTime]
                )
            '''
            diccio = None
            diccio = self.execute_queries_in_group(workspace_id, dataset_id, query)
            if diccio is None:
                print("Error getting tables from dataset.")
            return diccio
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_measures_from_dataset_in_group(self, workspace_id, dataset_id):
        """Get all measures from specific dataset in a workspace
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        ### Returns
        ----
        Response dict of measures from requests library. 200 OK
        """
        try:
            query = '''
            DEFINE
                VAR _tablas = SELECTCOLUMNS(INFO.TABLES(), "TableID", [ID], "Name", [Name])
                VAR _measures = SELECTCOLUMNS(INFO.MEASURES(), "TableID", [TableID], "MeasureID", [ID], "MeasureName", [Name], "DataType", [DataType], "Expression", [Expression] )
                VAR _ready_measures = SELECTCOLUMNS(NATURALINNERJOIN(_measures, _tablas), "TableID", [TableID], "Name", [Name], "ItemType", "Measure", "ItemID", [MeasureID], "ItemName", [MeasureName], "DataType", [DataType], "Expression", [Expression])
            EVALUATE 
                _ready_measures
            '''
            diccio = None
            diccio = self.execute_queries_in_group(workspace_id, dataset_id, query)
            if diccio is None:
                print("Error getting tables from dataset.")
            return diccio
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_columns_from_dataset_in_group(self, workspace_id, dataset_id):
        """Get all columns from specific dataset in a workspace
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL        
        ### Returns
        ----
        Response dict of measures from requests library. 200 OK
        """
        try:
            query = '''
            DEFINE
                VAR _tablas = SELECTCOLUMNS(INFO.TABLES(), "TableID", [ID], "Name", [Name])
                VAR _columnas = SELECTCOLUMNS(INFO.COLUMNS(), "TableID", [TableID], "ColumnID", [ID], "ColumnName", [ExplicitName], "ExplicitDataType", [ExplicitDataType])
                VAR _ready_columns = SELECTCOLUMNS(NATURALINNERJOIN(_columnas, _tablas), "TableID", [TableID], "Name", [Name], "ItemType", "Column", "ItemID", [ColumnID], "ItemName", [ColumnName], "ExplicitDataType", [ExplicitDataType], "Expression", "")
            EVALUATE 
                _ready_columns
            '''
            diccio = None
            diccio = self.execute_queries_in_group(workspace_id, dataset_id, query)
            if diccio is None:
                print("Error getting tables from dataset.")
            return diccio
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_roles_from_dataset_in_group(self, workspace_id, dataset_id):
        """Get all roles from specific dataset in a workspace
        ### Parameters
        ----
        workspace_id: str uuid
            The Power Bi workspace id. You can take it from PBI Service URL        
        dataset_id: str uuid
            The Power Bi Dataset id. You can take it from PBI Service URL                
        ### Limitations
        ----
            This request will only work for User and Password credentials. It won't work with Service Principal due to API limitations.
        ### Returns
        ----
        Response dict of measures from requests library. 200 OK
        """
        try:
            query = '''
            EVALUATE 
                INFO.ROLES()
            '''
            diccio = None
            diccio = self.execute_queries_in_group(workspace_id, dataset_id, query)
            if diccio is None:
                print("Error getting tables from dataset.")
            return diccio
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)