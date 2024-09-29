import os

from TechnicalSkillModel import TechnicalSkillModel
from basic_info_model import BasicInfoModel
from CollaborationTendencyModel import CollaborationTendencyModel


if __name__ == "__main__":
  
   '''replace with your github token'''
   token = os.getenv('GITHUB_TOKEN')
   if not token:
      raise ValueError("Please set the GITHUB_TOKEN environment variable.")
  
   '''replace with the user name you want to fetch'''
   user_login = "posva" # posva is an initial example
  
   dev_basic_model = BasicInfoModel(user_login=user_login, token=token)
   dev_tech_model = TechnicalSkillModel(user_login=user_login, token=token)
   #dev_collaboration_model = CollaborationTendencyModel(user_login=user_login, token=token)
  
   '''fetch the user basic info'''
   dev_basic_model.fetch_user_data()
  
   '''fetch the repos the user has contributed to and stored in a JSON file'''
   dev_tech_model.fetch_contributed_repositories()
  
   '''fetch topics for the contributed repositories and stored to a JSON file'''
   ''' make sure contributed_repos_file exists from previous step after running dev_tech_model.fetch_contributed_repositories(), the output should be stored in a json file, replace that file address'''
   contributed_repos_file = "./data_request/contributed_repos.json"  
   dev_tech_model.fetch_repo_topics(contributed_repos_file)
  
   '''fetch watched repositories and save to a JSON file'''
   dev_tech_model.fetch_watched_repositories()
  
   '''user-owned repositories'''
   dev_tech_model.fetch_user_owned_repositories()
  
 

