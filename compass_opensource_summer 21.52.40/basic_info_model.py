# basic_info_model.py
import requests
import json

url = "https://api.github.com/graphql"

class BasicInfoModel:
    def __init__(self, user_login, token) -> None:
        self.user_login = user_login
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def fetch_user_data(self):
        query = """
        query {
          user(login: "%s") {
            avatarUrl
            bio
            company
            email
            hasSponsorsListing
            location
            organizations(first: 3) {
              nodes {
                name
                url
              }
            }
          }
        }
        """ % self.user_login
        response = requests.post(url, json={'query': query}, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                print("API has returned errors.")
                return 
            
            if data.get('data') is None or data['data'].get('user') is None:
                print('Error Occurred: the user data is missing.')
                return 
            
            user_data = {
                "avatarUrl": data['data']['user']['avatarUrl'],
                "bio": data['data']['user']['bio'],
                "company": data['data']['user']['company'],
                "email": data['data']['user']['email'],
                "hasSponsorsListing": data['data']['user']['hasSponsorsListing'],
                "location": data['data']['user']['location'],
                "organizations": [
                    {
                        "name": org['name'],
                        "url": org['url']
                    } for org in data['data']['user']['organizations']['nodes']
                ]
            }

            output_file = f"./data_request/user_basic_info.json"
            with open(output_file, "w") as file:
                json.dump(user_data, file, indent=4)
                print(f"Output file saved to: {output_file}")
        else:
            print(f"Failed to fetch data, status code: {response.status_code}")
