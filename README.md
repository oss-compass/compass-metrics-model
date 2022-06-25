## Metrics Model
Metrics Model makes metrics combine  metrics together, you could find us [here](https://github.com/chaoss/wg-metrics-models) 

### please create conf.yaml file as following way:

    url:
        "https://user:password@ip:port"  
    params: 
        {
        'issue_index': Issue index  
        'json_file': json file for repos messages
        'git_index':  git index 
        'git_branch': None,
        'from_date': the beginning of time for metric model
        'end_date': the end of time for metric model
        'out_index': new index for metric model
        'community': the name of community
        'level': representation of the metrics, choose from repo, project, community.
        }

params is designed to init Metric Model. 