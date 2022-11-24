## Metrics Model 
Metrics Model makes metrics combine  metrics together, you could find us [here](https://github.com/chaoss/wg-metrics-models) 

### Please create json file as following way:
    
    {
      "gitee-{community name}": {
          "gitee-software-artifact": [
                "https://gitee.com/{owner}/{repo}"
          ],
          "gitee-governance": [
                "https://gitee.com/{owner}/{repo}"
          ]
      }
    }

If it is a github repository, you need to change gitee to github
### Please create conf.yaml file as following way:

    url:
        "https://user:password@ip:port"  
    params: 
        {
            'issue_index': Issue index,
            'pr_index':pr index, 
            'json_file': json file for repos messages,
            'git_index': git index,
            'git_branch': git branch,
            'from_date': the beginning of time for metric model,
            'end_date': the end of time for metric model,
            'out_index': new index for metric model,
            'community': the name of community,
            'level': representation of the metrics, choose from repo, project, community,
            'company': the name of company,
            'pr_comments_index': pr comment index,
            'issue_comments_index': issue comment index,
            'repo_index': repo index,
            'release_index': release index
        }

params is designed to init Metric Model. 

###  Modify 'cofig_url' path in the run.py , Run metrics model
    
    python run.py
    
