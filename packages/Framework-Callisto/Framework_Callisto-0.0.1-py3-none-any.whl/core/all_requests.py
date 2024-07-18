import requests 

#Here we gonna implement the different Requests. Get, Post, Delete , Put, Patch
url = 'https://sso-int.mercedes-benz.com/as/token.oauth2'


# Credentials
client_id = "66237693-8c39-4c35-bb0a-a4509a601e4d"
client_secret = "e3e4ba52-e259-4dfd-bf90-99d4f92fe00e"



heading = {
    'Content-Type': 'application/x-www-form-urlencoded', 
    'accept': 'application/text'
}


dating = { 
    "client_id": client_id,
    "client_secret":  client_secret,
    "grant_type": "client_credentials"
       }


def post_request(client_id_parameter,client_secret_parameter):
    output = requests.post(url,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,verify=False)
    
    return output.content 


def get_request(url_parmeter,client_id_parameter,client_secret_parameter):
    output = requests.get(url_parmeter,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,verify=False) 
    return output.content 


def delete_request(url_parmeter,client_id_parameter,client_secret_parameter):
    output = requests.delete(url_parmeter,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,verify=False)
    return output.content 


# The payload is the parameter that you need to 
def put_request(url_parmeter,payload,client_id_parameter,client_secret_parameter):
    output = requests.put(url_parmeter,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,data = payload,verify=False)
    return  output.content 


# Printout the status code
def head_request(url_parmeter,payload,client_id_parameter,client_secret_parameter):
    output = requests.head(url_parmeter,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,data = payload,verify=False)
    return  output.content 


# Printout the status code
def head_request(url_parmeter,client_id_parameter,client_secret_parameter):
    output = requests.head(url_parmeter,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,verify=False)
    return  output


# Printout the status code
def patch_request(url_parmeter,payload,client_id_parameter,client_secret_parameter):
    output = requests.head(url_parmeter,data={ 
    "client_id": client_id_parameter,
    "client_secret":  client_secret_parameter,
    "grant_type": "client_credentials"
       } ,headers=heading,data = payload,verify=False)
    return  output
