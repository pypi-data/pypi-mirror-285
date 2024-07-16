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
@........|____| |  | |...*   *.@    Copyright © 2024 Ignacio Barrau
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

class Items():
    """Simple library to use the  api and obtain items from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request fabric item API
        Args:
            token: String
                Bearer Token to use the Rest API
        """
        self.token = token
            
    def get_item_in_group(self, workspace_id, item_id):
        """Returns the specified item from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a item in the workspace.
        ### Limitations
        ----
        This API is supported for a number of item types, find the supported item types here.
        https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/item-management-overview
        """
        try:
            url = "https://api.fabric.microsoft.com/v1/workspaces/{}/items/{}".format(workspace_id, item_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
                      
    def list_items(self, workspace_id):
        """Returns a list of items from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing all the items in the workspace.
        """
        try:
            url = "https://api.fabric.microsoft.com/v1/workspaces/{}/items".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
                       
    def delete_item_in_group(self, workspace_id, item_id):
        """Deletes the specified item from the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        ### Returns
        ----
        Response object from requests library. 200 OK
        
        """
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/items/{}".format(workspace_id, item_id)   
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
            res = requests.delete(url, headers=headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def create_item(self, workspace_id, item_id, displayName, itemType, description=None):
        """Creates an item in the specified workspace. Preview request, soon we'll add 'definition' parameter
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        displayName: str
            The item display name. The display name must follow naming rules according to item type.
        itemType: str
            The item type. Example: Dashboard, DataPipeline, Datamart, Eventstream, KQLDataConnection, KQLDatabase, KQLQueryset, Lakehouse, MLExperiment, MLModel, MountedWarehouse, Notebook, PaginatedReport, Report, SQLEndpoint, SemanticModel, SparkJobDefinition
        description: str
            The item description. Max length is 256 characters.
        ### Returns
        ----
        Response object from requests library. 201 or 202 OK
        ### Limitations
        ----
        To create a non-PowerBI Fabric item the workspace must be on a supported Fabric capacity type. For more information see Microsoft Fabric license types.
To create a PowerBI item, the user must have the appropritate license. For more information see Microsoft Fabric license types.
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/items".format(workspace_id)
            body = {
                "displayName": displayName,
                "type": itemType
            }
            if description != None:
                body["description"]=description
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_item_definition(self, workspace_id, item_id):
        """Returns the specified item definition.
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL        
        ### Returns
        ----
        Response object from requests library. 200 OK        
        ### Limitations
        ----
        This API is blocked for an item with an encrypted sensitivity label.
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items/{}/getDefinition".format(workspace_id, item_id)
            body = {
                "displayName": displayName,
                "type": item_type
            }
            if description != None:
                body["description"]=description
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_item(self, workspace_id, item_id, displayName=None, description=None):
        """Updates the properties of the specified item.
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        displayName: str
            The item display name. The display name must follow naming rules according to item type.
        description: str
            The item description. Max length is 256 characters.
        ### Returns
        ----
        Response object from requests library. 200 OK
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/items/{}".format(workspace_id, item_id)
            body = {}
            if displayName != None:
                body["displayName"]=displayName
            if description != None:
                body["description"]=description
            if body == {}:
                raise Exception("Please specify a display name or description to update item.")
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.patch(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_item_definition(self, workspace_id, item_id, parts, format=None):
        """Overrides the definition for the specified item.
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        parts: ItemDefinitionPart[]
            A list of definition parts. part, payload and payloadtype description. Read API Docs for more details.
        format: str 
            	The format of the item definition.
        
        ### Returns
        ----
        Response object from requests library. 200 OK
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/items/{}/updateDefinition".format(workspace_id, item_id)
            body = {
                "definition": {
                    "parts": parts
                    }
            }
            if format != None:
                body["format"]=format
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
       
class Git():
    """Simple library to use the  api and obtain items from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request fabric item API
        Args:
            token: String
                Bearer Token to use the Rest API
        """
        self.token = token
            
    def get_git_connection(self, workspace_id):
        """Returns git connection details for the specified workspace.
        ### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a item in the workspace.
        """
        try:
            url = "https://api.fabric.microsoft.com/v1/workspaces/{}/git/connection".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def get_git_status(self, workspace_id):
        """Returns the Git status of items in the workspace, that can be committed to Git.
        ### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        ### Returns
        ----
        Dict:
            A dictionary containing a item in the workspace.
        """
        try:
            url = "https://api.fabric.microsoft.com/v1/workspaces/{}/git/status".format(workspace_id)
            res = requests.get(url, headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)})
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def commit_to_git(self, workspace_id, mode, comment, workspaceHead, items=None):
        """Commits the changes made in the workspace to the connected remote branch.
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        mode: string
            The mode for the commit operation.
        comment: string
            	Caller-free comment for this commit. Maximum length is 300 characters. If no comment is provided by the caller, use the default Git provider comment.
        workspaceHead: str 
            	Full SHA hash that the workspace is synced to. The hash can be retrieved from the Git Status API.
        items: itemsIdentifier[]
            Specific items to commit. This is relevant only for Selective commit mode. The items can be retrieved from the Git Status API.
            Each item it's { "logicalId": str uuid, "objectId": str uud }. You can use one of them or both if you have them.
        ### Returns
        ----
        Response object from requests library. 202 OK
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/git/commitToGit".format(workspace_id)
            body = {
                "mode": mode,
                "workspaceHead": workspaceHead,
                "comment": comment
            }
            if items != None:
                body["items"]=items
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
    def update_from_git(self, workspace_id, item_id, remoteCommitHash, conflictResolution, allowOverrideItems, workspaceHead):
        """Updates the workspace with commits pushed to the connected branch.
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        remoteCommitHash: string
            	Remote full SHA commit hash.
        conflictResolution: string
            	Conflict resolution to be used in the update from Git operation. If items are in conflict and a conflict resolution is not specified, the update operation will not start. Example:
            {"ConflictResolutionPolicy": PreferRemote or PreferWorkspace, "ConflictResolutionType": "Workspace"}
        options: options
            Automatically written by simplepbi. Options to be used in the update from Git operation. For now just overrideitems
        allowOverrideItems: bool
            User consent to override incoming items during the update from Git process. When incoming items are present and the allow override items is not specified or is provided as false, the update operation will not start. Default value is false.
        workspace_head: str 
            	Full SHA hash that the workspace is synced to. The hash can be retrieved from the Git Status API.
        ### Returns
        ----
        Response object from requests library. 202 OK
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/items/{}/git/updateFromGit".format(workspace_id, item_id)
            body = {
                "workspaceHead": workspaceHead,
                "remoteCommitHash": remoteCommitHash,
                "conflictResolution": conflictResolution,
                "options":{
                    "allowOverrideItems": allowOverrideItems
                }
            }
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
class Scheduler():

    """Simple library to use the api and obtain job scheduler from it.
    """

    def __init__(self, token):
        """Create a simplePBI object to request fabric job scheduler API
        Args:
            token: String
                Bearer Token to use the Rest API
        """
        self.token = token
        
    def run_on_demand_item_job(self, workspace_id, item_id, jobType):
        """Run on-demand item job instance.
        #### Parameters
        ----
        workspace_id: str uuid
            The workspace id. You can take it from PBI Service URL
        item_id: str uuid
            The item id. You can take it from PBI Service URL
        jobType: string
            The job type, for now just "DefaultJob"
        executionData: str 
            	Execution data for the job. Preview parameter, a working progress from the API      
        ### Returns
        ----
        Response object from requests library. 202 OK
        """
        
        try: 
            url= "https://api.fabric.microsoft.com/v1/workspaces/{}/items/{}/jobs/instances?jobType={}".format(workspace_id, item_id, jobType)
            body = {
                "executionData": {}
            }
            if format != None:
                body["format"]=format
            headers={'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}            
            res = requests.post(url, data = json.dumps(body), headers = headers)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as ex:
            print("HTTP Error: ", ex, "\nText: ", ex.response.text)
        except requests.exceptions.RequestException as e:
            print("Request exception: ", e)
            
            