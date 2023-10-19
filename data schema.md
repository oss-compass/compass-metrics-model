# Raw Data
# git data

index : gitee-git_raw, github-git_raw

```
 {
    "_index" : "gitee-git_raw",  //index名称
    "_id" : "bb6658ca89bdb1109d125b2d2b73051ea469bf50",  //id
    "_score" : 1.0,  //文档的相关性得分
    "_source" : {
        "backend_name" : "Git",  //backend名称 (Git, Gitee, Github)
        "backend_version" : "0.12.1",  //backend版本
        "perceval_version" : "0.20.0-rc.9",  //perceval版本
        "timestamp" : 1.663685974201459E9,  //raw数据收集时间戳(对应metadata__timestamp)
        "origin" : "https://gitee.com/lishengbao/python_test.git", //仓库地址
        "uuid" : "bb6658ca89bdb1109d125b2d2b73051ea469bf50",  //uuid
        "updated_on" : 1.658978327E9,  //数据更新的时间戳(对应metadata__updated_on)
        "classified_fields_filtered" : null,  //过滤分类字段
        "category" : "commit",  //分类(commit, repository, issue, pull_request)
        "search_fields" : {  //搜索字段信息
            "item_id" : "cd3523665deeac1fe7833d9d761b4167ae369129"
        },
        "tag" : "https://gitee.com/lishengbao/python_test.git",  //仓库地址(跟origin一样)
        "data" : {
            "commit" : "cd3523665deeac1fe7833d9d761b4167ae369129",  //commit id(commit hash)
            "parents" : [ ],  //上一个commit id
            "refs" : [ 
                "HEAD -> refs/heads/master"  //当前HEAD指向哪个分支
            ],  
            "Author" : "lishengbao <563167901@qq.com>",  //作者名称和邮箱(代码编写者)
            "AuthorDate" : "Thu Jul 28 03:18:47 2022 +0000",  //作者时间(代码编写者)
            "Commit" : "Gitee <noreply@gitee.com>",  //提交者的名称和邮箱
            "CommitDate" : "Thu Jul 28 03:18:47 2022 +0000",  //commit提交时间
            "message" : "Initial commit",   //commit描述
            "files" : [  //文件的变化情况
                {
                "modes" : [  //文件属性
                    "000000",  //区分文件类型
                    "100644"
                ],
                "indexes" : [
                    "0000000",
                    "fe92650"
                ],
                "action" : "A",   //M:Modify A:Add D:Delete
                "file" : "README.en.md",  //发生修改的文件名
                "added" : "36",  //文件新增行数
                "removed" : "0"  //文件减少行数
                },
                {
                "modes" : [
                    "000000",
                    "100644"
                ],
                "indexes" : [
                    "0000000",
                    "e68c380"
                ],
                "action" : "A",
                "file" : "README.md",
                "added" : "39",
                "removed" : "0"
                }
            ]
        },
        "metadata__updated_on" : "2022-07-28T03:18:47+00:00",  //数据更新时间
        "metadata__timestamp" : "2022-09-20T14:59:34.201459+00:00"  //raw数据收集时的时间
    }
}
```
# repo data

index : gitee-repo_raw, github-repo_raw

```
{
  "_index" : "gitee-repo_raw",   //index名称
  "_id" : "258d5cf635e3f38c5699161cb4ff9904f4db4d7f",  //id
  "_score" : 6.2058125,  //文档的相关性得分
  "_source" : {
    "backend_name" : "Gitee",  //backend名称 (Git, Gitee, Github)
    "backend_version" : "0.1.0",  //backend版本
    "perceval_version" : "0.20.0-rc.9",  //perceval版本
    "timestamp" : 1.663169764302843E9,  //raw数据收集时间戳(对应metadata__timestamp)
    "origin" : "https://gitee.com/mindspore/mindspore",  //仓库地址
    "uuid" : "258d5cf635e3f38c5699161cb4ff9904f4db4d7f",  //uuid
    "updated_on" : 1.663169764302824E9,  //数据更新的时间戳(对应metadata__updated_on)
    "classified_fields_filtered" : null,  //过滤分类字段
    "category" : "repository",  //分类(commit, repository, issue, pull_request)
    "search_fields" : {  //搜索字段信息
      "item_id" : "1663169764.302824",
      "owner" : "mindspore",
      "repo" : "mindspore"
    },
    "tag" : "https://gitee.com/mindspore/mindspore",  //仓库地址(跟origin一样)
    "data" : {
      "id" : 8649239,  //仓库id
      "full_name" : "mindspore/mindspore",  //仓库空间名称
      "human_name" : "MindSpore/mindspore",  //仓库名称(用户可修改的)
      "url" : "https://gitee.com/api/v5/repos/mindspore/mindspore",  //获取仓库数据url
      "namespace" : {
        "id" : 6854763,    //namespace id
        "type" : "group",  //namespace 类型 企业:Enterprise  组织:Group 用户:null
        "name" : "MindSpore",  //namespace 名称
        "path" : "mindspore", //namespace 路径
        "html_url" : "https://gitee.com/mindspore", //namespace 地址
        "parent" : {
          "id" : 5439905,
          "type" : "enterprise",
          "name" : "MindSpore",
          "path" : "mind_spore",
          "html_url" : "https://gitee.com/mind_spore"
        }
      },
      "path" : "mindspore",  //仓库路径
      "name" : "mindspore",  //仓库名称
      "owner" : {
        "id" : 6560119,
        "login" : "zhunaipan",
        "name" : "zhunaipan",
        "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/2186/6560119_panza_1584156773.png",
        "url" : "https://gitee.com/api/v5/users/zhunaipan",
        "html_url" : "https://gitee.com/zhunaipan",
        "remark" : "",
        "followers_url" : "https://gitee.com/api/v5/users/zhunaipan/followers",
        "following_url" : "https://gitee.com/api/v5/users/zhunaipan/following_url{/other_user}",
        "gists_url" : "https://gitee.com/api/v5/users/zhunaipan/gists{/gist_id}",
        "starred_url" : "https://gitee.com/api/v5/users/zhunaipan/starred{/owner}{/repo}",
        "subscriptions_url" : "https://gitee.com/api/v5/users/zhunaipan/subscriptions",
        "organizations_url" : "https://gitee.com/api/v5/users/zhunaipan/orgs",
        "repos_url" : "https://gitee.com/api/v5/users/zhunaipan/repos",
        "events_url" : "https://gitee.com/api/v5/users/zhunaipan/events{/privacy}",
        "received_events_url" : "https://gitee.com/api/v5/users/zhunaipan/received_events",
        "type" : "User"
      },  //Owner用户信息(组织的Owner信息)
      "assigner" : {
        "id" : 5625371,
        "login" : "iambowen1984",
        "name" : "iambowen1984",
        "avatar_url" : "https://gitee.com/assets/no_portrait.png",
        "url" : "https://gitee.com/api/v5/users/iambowen1984",
        "html_url" : "https://gitee.com/iambowen1984",
        "remark" : "",
        "followers_url" : "https://gitee.com/api/v5/users/iambowen1984/followers",
        "following_url" : "https://gitee.com/api/v5/users/iambowen1984/following_url{/other_user}",
        "gists_url" : "https://gitee.com/api/v5/users/iambowen1984/gists{/gist_id}",
        "starred_url" : "https://gitee.com/api/v5/users/iambowen1984/starred{/owner}{/repo}",
        "subscriptions_url" : "https://gitee.com/api/v5/users/iambowen1984/subscriptions",
        "organizations_url" : "https://gitee.com/api/v5/users/iambowen1984/orgs",
        "repos_url" : "https://gitee.com/api/v5/users/iambowen1984/repos",
        "events_url" : "https://gitee.com/api/v5/users/iambowen1984/events{/privacy}",
        "received_events_url" : "https://gitee.com/api/v5/users/iambowen1984/received_events",
        "type" : "User"
      },  //Assigner用户信息(仓库创建者信息)
      "description" : "MindSpore is a new open source deep learning training/inference framework that could be used for mobile, edge and cloud scenarios.", //仓库描述
      "private" : false, //仓库是否私有
      "public" : true,  //仓库是否公开
      "internal" : false,  //是否内部开源
      "fork" : false,  //是否是fork仓库
      "html_url" : "https://gitee.com/mindspore/mindspore.git",  //仓库html地址
      "ssh_url" : "git@gitee.com:mindspore/mindspore.git",  //仓库ssh地址
      "forks_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/forks",
      "keys_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/keys{/key_id}",
      "collaborators_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/collaborators{/collaborator}",
      "hooks_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/hooks",
      "branches_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/branches{/branch}",
      "tags_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/tags",
      "blobs_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/blobs{/sha}",
      "stargazers_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/stargazers",
      "contributors_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/contributors",
      "commits_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/commits{/sha}",
      "comments_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/comments{/number}",
      "issue_comment_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/issues/comments{/number}",
      "issues_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/issues{/number}",
      "pulls_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls{/number}",
      "milestones_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/milestones{/number}",
      "notifications_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/notifications{?since,all,participating}",
      "labels_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/labels{/name}",
      "releases_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/releases{/id}",
      "recommend" : true,  //是否是推荐仓库
      "gvp" : true,  //是否是 GVP 仓库
      "homepage" : "https://www.mindspore.cn",  //主页
      "language" : "Python",   //语言
      "forks_count" : 3189,  //仓库fork数量
      "stargazers_count" : 6904,   //仓库star数量
      "watchers_count" : 1873,  //仓库watch数量
      "default_branch" : "master",  //默认分支
      "open_issues_count" : 1426,  //开启的issue数量
      "has_issues" : true, //是否开启issue功能
      "has_wiki" : true,  //是否开启Wiki功能
      "issue_comment" : false,  //是否允许用户对“关闭”状态的 Issue 进行评论
      "can_comment" : false,  //是否允许用户对仓库进行评论
      "pull_requests_enabled" : true,  //是否接受 Pull Request，协作开发
      "has_page" : false,  //是否开启了 Pages
      "license" : "Apache-2.0",  //开源许可
      "outsourced" : false,  //仓库类型（针对企业内部/外包）
      "project_creator" : "iambowen1984",  //仓库创建者的 username
      "members" : [
        "youui",
        "yingjy"
      ],  //仓库成员的username
      "pushed_at" : "2022-09-14T21:51:25+08:00",  //最近一次代码推送时间
      "created_at" : "2020-03-27T11:47:45+08:00", //仓库创建时间
      "updated_at" : "2022-09-14T23:07:31+08:00", //仓库最近更新时间
      "parent" : null,  //父级仓库信息
      "paas" : null,
      "stared" : false,  //是否 star(是否该token star)
      "watched" : false,  //是否 watch
      "permission" : {
        "pull" : true,
        "push" : false,
        "admin" : false
      },  //操作权限
      "relation" : null,  //当前用户相对于仓库的角色(当前token)
      "assignees_number" : 0,  //代码审查人数
      "testers_number" : 0,   //代码测试人数
      "assignee" : [
        {
          "id" : 6517837,
          "login" : "kingxian",
          "name" : "kingxian",
          "avatar_url" : "https://gitee.com/assets/no_portrait.png",
          "url" : "https://gitee.com/api/v5/users/kingxian",
          "html_url" : "https://gitee.com/kingxian",
          "remark" : "",
          "followers_url" : "https://gitee.com/api/v5/users/kingxian/followers",
          "following_url" : "https://gitee.com/api/v5/users/kingxian/following_url{/other_user}",
          "gists_url" : "https://gitee.com/api/v5/users/kingxian/gists{/gist_id}",
          "starred_url" : "https://gitee.com/api/v5/users/kingxian/starred{/owner}{/repo}",
          "subscriptions_url" : "https://gitee.com/api/v5/users/kingxian/subscriptions",
          "organizations_url" : "https://gitee.com/api/v5/users/kingxian/orgs",
          "repos_url" : "https://gitee.com/api/v5/users/kingxian/repos",
          "events_url" : "https://gitee.com/api/v5/users/kingxian/events{/privacy}",
          "received_events_url" : "https://gitee.com/api/v5/users/kingxian/received_events",
          "type" : "User"
        }
      ],  //代码审查用户信息
      "enterprise" : { 
        "id" : 5439905,  //id
        "type" : "enterprise",  //类型，企业：Enterprise，组织：Group，用户：null
        "name" : "MindSpore",  //名称
        "path" : "mind_spore",  //路径
        "html_url" : "https://gitee.com/mind_spore"  //地址
      },  //企业信息
      "project_labels" : [ ],  //仓库标签
      "releases" : [
        {
          "id" : 62730,  //release id
          "tag_name" : "v0.1.0-alpha",  //release 名称
          "target_commitish" : "576a73b42a34a32b6bda6af262df1735a47d2e98",  //对应的commit
          "prerelease" : false,  //是否预发版本
          "name" : "v0.1.0-alpha",  //release 名称
          "body" : "# Release 0.1.0-alpha.....",  //release body
          "author" : {  //作者用户信息
            "id" : 6560119,
            "login" : "zhunaipan",
            "name" : "zhunaipan",
            "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/2186/6560119_panza_1584156773.png",
            "url" : "https://gitee.com/api/v5/users/zhunaipan",
            "html_url" : "https://gitee.com/zhunaipan",
            "remark" : "",
            "followers_url" : "https://gitee.com/api/v5/users/zhunaipan/followers",
            "following_url" : "https://gitee.com/api/v5/users/zhunaipan/following_url{/other_user}",
            "gists_url" : "https://gitee.com/api/v5/users/zhunaipan/gists{/gist_id}",
            "starred_url" : "https://gitee.com/api/v5/users/zhunaipan/starred{/owner}{/repo}",
            "subscriptions_url" : "https://gitee.com/api/v5/users/zhunaipan/subscriptions",
            "organizations_url" : "https://gitee.com/api/v5/users/zhunaipan/orgs",
            "repos_url" : "https://gitee.com/api/v5/users/zhunaipan/repos",
            "events_url" : "https://gitee.com/api/v5/users/zhunaipan/events{/privacy}",
            "received_events_url" : "https://gitee.com/api/v5/users/zhunaipan/received_events",
            "type" : "User"
          },
          "created_at" : "2020-03-27T21:13:11+08:00",  //创建时间
          "assets" : [
            {
              "browser_download_url" : "https://gitee.com/mindspore/mindspore/archive/refs/tags/v0.1.0-alpha.zip"  //资源包下载地址
            }
          ]
        }
      ], 
      "fetched_on" : 1.663169764302824E9  //raw收集时间
    },
    "metadata__updated_on" : "2022-09-14T15:36:04.302824+00:00",  //数据更新时间
    "metadata__timestamp" : "2022-09-14T15:36:04.302843+00:00"  //raw数据收集时的时间
  }
}

```
# issue data

index : gitee-issues_raw, github-issues_raw

```

{
    "_index" : "gitee-issues_raw",  //index名称
    "_id" : "fc96ee418df32b4a4b2d23f8569152cccc60a7d3",  //id
    "_score" : null,
    "_source" : {
        "backend_name" : "Gitee",  //backend名称(Git, Gitee, Github)
        "backend_version" : "0.1.0",  //backend版本
        "perceval_version" : "0.20.0-rc.9",   //perceval版本
        "timestamp" : 1.668591041604659E9,  //raw数据收集时间戳(对应metadata__timestamp)
        "origin" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址
        "uuid" : "fc96ee418df32b4a4b2d23f8569152cccc60a7d3",  //uuid
        "updated_on" : 1.668589619E9,  //数据更新的时间戳(对应metadata__updated_on)
        "classified_fields_filtered" : null,  //过滤分类字段
        "category" : "issue",  //分类(commit, repository, issue, pull_request)
        "search_fields" : {
        "item_id" : "10108112",
        "owner" : "opengauss",
        "repo" : "openGauss-server"
        },  //搜索字段信息
        "tag" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址(跟origin一样)
        "data" : {
            "id" : 10108112,   //issue id
            "url" : "https://gitee.com/api/v5/enterprises/opengaussorg/issues/I60NGW",  //获取issue数据url
            "repository_url" : "https://gitee.com/api/v5/enterprises/opengaussorg",  //获取repo url
            "labels_url" : "https://gitee.com/api/v5/enterprises/opengaussorg/issues/I60NGW/labels",  //获取issue标签url
            "comments_url" : "https://gitee.com/api/v5/enterprises/opengaussorg/issues/I60NGW/comments", //获取issue评论 url
            "html_url" : "https://gitee.com/opengauss/openGauss-server/issues/I60NGW",  //获取issue html页面url
            "parent_url" : null,  //上级issue url(企业)
            "number" : "I60NGW",  //issue 编号
            "parent_id" : 0,  //上级id
            "depth" : 0,  //所在层级
            "state" : "progressing",  //Issue的状态: open（开启的）, progressing(进行中), closed（关闭的）, rejected（拒绝的）
            "title" : "copy 指令帮助信息与文档不一致",  //issue 标题
            "body" : "【标题描述】:如图，copy指令的帮助信息与文档，总共有 12 处不一致。",  //issue body
            "user" : {  //提交issue用户信息
                "id" : 6529967,
                "login" : "dodders",
                "name" : "laishenghao",
                "avatar_url" : "https://foruda.gitee.com/avatar/1662526216905766118/6529967_dodders_1662526216.png",
                "url" : "https://gitee.com/api/v5/users/dodders",
                "html_url" : "https://gitee.com/dodders",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/dodders/followers",
                "following_url" : "https://gitee.com/api/v5/users/dodders/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/dodders/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/dodders/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/dodders/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/dodders/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/dodders/repos",
                "events_url" : "https://gitee.com/api/v5/users/dodders/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/dodders/received_events",
                "type" : "User"
            },
            "labels" : [ ],  //issue的label
            "assignee" : {   //issue负责人信息
                "id" : 6529967,
                "login" : "dodders",
                "name" : "laishenghao",
                "avatar_url" : "https://foruda.gitee.com/avatar/1662526216905766118/6529967_dodders_1662526216.png",
                "url" : "https://gitee.com/api/v5/users/dodders",
                "html_url" : "https://gitee.com/dodders",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/dodders/followers",
                "following_url" : "https://gitee.com/api/v5/users/dodders/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/dodders/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/dodders/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/dodders/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/dodders/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/dodders/repos",
                "events_url" : "https://gitee.com/api/v5/users/dodders/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/dodders/received_events",
                "type" : "User"
            },
            "collaborators" : [ ],  //issue 合作者信息
            "repository" : {  //issue所属repo信息
                "id" : 10088393,
                "full_name" : "opengauss/openGauss-server",
                "human_name" : "openGauss/openGauss-server",
                "url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server",
                "namespace" : {
                    "id" : 5549555,
                    "type" : "group",
                    "name" : "openGauss",
                    "path" : "opengauss",
                    "html_url" : "https://gitee.com/opengauss"
                },
                "path" : "openGauss-server",
                "name" : "openGauss-server",
                "owner" : {
                    "id" : 5227357,
                    "login" : "xiangxinyong",
                    "name" : "xiangxinyong",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/1742/5227357_xiangxinyong_1578982846.png",
                    "url" : "https://gitee.com/api/v5/users/xiangxinyong",
                    "html_url" : "https://gitee.com/xiangxinyong",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/xiangxinyong/followers",
                    "following_url" : "https://gitee.com/api/v5/users/xiangxinyong/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/xiangxinyong/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/xiangxinyong/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/xiangxinyong/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/xiangxinyong/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/xiangxinyong/repos",
                    "events_url" : "https://gitee.com/api/v5/users/xiangxinyong/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/xiangxinyong/received_events",
                    "type" : "User"
                },
                "assigner" : {
                    "id" : 5227357,
                    "login" : "xiangxinyong",
                    "name" : "xiangxinyong",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/1742/5227357_xiangxinyong_1578982846.png",
                    "url" : "https://gitee.com/api/v5/users/xiangxinyong",
                    "html_url" : "https://gitee.com/xiangxinyong",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/xiangxinyong/followers",
                    "following_url" : "https://gitee.com/api/v5/users/xiangxinyong/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/xiangxinyong/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/xiangxinyong/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/xiangxinyong/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/xiangxinyong/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/xiangxinyong/repos",
                    "events_url" : "https://gitee.com/api/v5/users/xiangxinyong/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/xiangxinyong/received_events",
                    "type" : "User"
                },
                "description" : "openGauss kernel ~ openGauss is an open source relational database management system.",
                "private" : false,
                "public" : true,
                "internal" : false,
                "fork" : false,
                "html_url" : "https://gitee.com/opengauss/openGauss-server.git",
                "ssh_url" : "git@gitee.com:opengauss/openGauss-server.git",
                "forks_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/forks",
                "keys_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/keys{/key_id}",
                "collaborators_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/collaborators{/collaborator}",
                "hooks_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/hooks",
                "branches_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/branches{/branch}",
                "tags_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/tags",
                "blobs_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/blobs{/sha}",
                "stargazers_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/stargazers",
                "contributors_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/contributors",
                "commits_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/commits{/sha}",
                "comments_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/comments{/number}",
                "issue_comment_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/issues/comments{/number}",
                "issues_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/issues{/number}",
                "pulls_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/pulls{/number}",
                "milestones_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/milestones{/number}",
                "notifications_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/notifications{?since,all,participating}",
                "labels_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/labels{/name}",
                "releases_url" : "https://gitee.com/api/v5/repos/opengauss/openGauss-server/releases{/id}",
                "recommend" : true,
                "gvp" : true,
                "homepage" : null,
                "language" : "C++",
                "forks_count" : 952,
                "stargazers_count" : 1008,
                "watchers_count" : 339,
                "default_branch" : "master",
                "open_issues_count" : 526,
                "has_issues" : true,
                "has_wiki" : true,
                "issue_comment" : false,
                "can_comment" : false,
                "pull_requests_enabled" : true,
                "has_page" : false,
                "license" : "MulanPSL-2.0",
                "outsourced" : false,
                "project_creator" : "xiangxinyong",
                "members" : [
                    "jianfenglee",
                    "xiangxinyong"
                ],
                "pushed_at" : "2022-11-16T14:23:35+08:00",
                "created_at" : "2020-06-30T17:32:18+08:00",
                "updated_at" : "2022-11-16T17:24:49+08:00",
                "parent" : null,
                "paas" : null,
                "assignees_number" : 0,
                "testers_number" : 0,
                "assignee" : [ ],
                "testers" : [ ],
                "status" : "开始",
                "programs" : [
                {
                    "id" : 361110,
                    "name" : "openGauss 3.0.0 community",
                    "description" : "",
                    "assignee" : {
                    "id" : 7758693,
                    "login" : "cyj10727",
                    "name" : "蔡亚杰",
                    "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                    "url" : "https://gitee.com/api/v5/users/cyj10727",
                    "html_url" : "https://gitee.com/cyj10727",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/cyj10727/followers",
                    "following_url" : "https://gitee.com/api/v5/users/cyj10727/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/cyj10727/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/cyj10727/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/cyj10727/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/cyj10727/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/cyj10727/repos",
                    "events_url" : "https://gitee.com/api/v5/users/cyj10727/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/cyj10727/received_events",
                    "type" : "User"
                    }
                }
                ],
                "enterprise" : {
                "id" : 5961634,
                "type" : "enterprise",
                "name" : "openGauss",
                "path" : "opengaussorg",
                "html_url" : "https://gitee.com/opengaussorg"
                },
                "project_labels" : [ ]
            },
            "milestone" : null,  //issue关联的里程碑
            "created_at" : "2022-11-11T11:42:33+08:00", //issue 创建时间
            "updated_at" : "2022-11-16T17:06:59+08:00",  //issue 更新时间
            "plan_started_at" : null,  //计划开始时间
            "deadline" : null,  //计划结束时间
            "finished_at" : null,  //完成时间
            "scheduled_time" : 0,  //预计工期
            "comments" : 2,  //评论数量
            "priority" : 2,  //优先级(0: 不指定 1: 不重要 2: 次要 3: 主要 4: 严重)
            "issue_type" : "缺陷",  //issue类型
            "program" : {  //issue 关联的项目信息
                "id" : 451125,
                "name" : "openGauss 3.1.1 community",
                "description" : "",
                "assignee" : {
                    "id" : 8432190,
                    "login" : "flowill",
                    "name" : "Will",
                    "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                    "url" : "https://gitee.com/api/v5/users/flowill",
                    "html_url" : "https://gitee.com/flowill",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/flowill/followers",
                    "following_url" : "https://gitee.com/api/v5/users/flowill/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/flowill/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/flowill/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/flowill/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/flowill/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/flowill/repos",
                    "events_url" : "https://gitee.com/api/v5/users/flowill/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/flowill/received_events",
                    "type" : "User"
                },
                "author" : {
                    "id" : 8432190,
                    "login" : "flowill",
                    "name" : "Will",
                    "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                    "url" : "https://gitee.com/api/v5/users/flowill",
                    "html_url" : "https://gitee.com/flowill",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/flowill/followers",
                    "following_url" : "https://gitee.com/api/v5/users/flowill/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/flowill/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/flowill/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/flowill/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/flowill/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/flowill/repos",
                    "events_url" : "https://gitee.com/api/v5/users/flowill/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/flowill/received_events",
                    "type" : "User"
                }
            },
            "security_hole" : false,  //issue是否为私有
            "issue_state" : "修复中",   //issue 状态
            "branch" : null,  //分支
            "issue_type_detail" : {
                "id" : 190710,
                "title" : "缺陷",
                "template" : "<!-- #请根据issue的类型在标题左侧下拉框中选择对应的选项（需求、缺陷或咨询等）-->",
                "ident" : "bug",
                "color" : "#EF0016",
                "is_system" : true,
                "created_at" : "2020-04-14T09:54:20+08:00",
                "updated_at" : "2022-04-02T10:30:23+08:00"
            },
            "user_data" : {  //提交issue用户信息(更详细)
                "id" : 6529967,
                "login" : "dodders",
                "name" : "laishenghao",
                "avatar_url" : "https://foruda.gitee.com/avatar/1662526216905766118/6529967_dodders_1662526216.png",
                "url" : "https://gitee.com/api/v5/users/dodders",
                "html_url" : "https://gitee.com/dodders",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/dodders/followers",
                "following_url" : "https://gitee.com/api/v5/users/dodders/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/dodders/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/dodders/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/dodders/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/dodders/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/dodders/repos",
                "events_url" : "https://gitee.com/api/v5/users/dodders/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/dodders/received_events",
                "type" : "User",
                "blog" : null,
                "weibo" : null,
                "bio" : "",
                "public_repos" : 11,
                "public_gists" : 0,
                "followers" : 0,
                "following" : 2,
                "stared" : 7,
                "watched" : 93,
                "created_at" : "2020-03-07T17:29:46+08:00",
                "updated_at" : "2022-11-09T11:03:12+08:00",
                "company" : null,
                "profession" : null,
                "wechat" : null,
                "qq" : null,
                "linkedin" : null,
                "email" : null,
                "organizations" : [ ]
            },
            "assignee_data" : {  //issue负责人信息(更详细)
                "id" : 6529967,
                "login" : "dodders",
                "name" : "laishenghao",
                "avatar_url" : "https://foruda.gitee.com/avatar/1662526216905766118/6529967_dodders_1662526216.png",
                "url" : "https://gitee.com/api/v5/users/dodders",
                "html_url" : "https://gitee.com/dodders",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/dodders/followers",
                "following_url" : "https://gitee.com/api/v5/users/dodders/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/dodders/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/dodders/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/dodders/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/dodders/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/dodders/repos",
                "events_url" : "https://gitee.com/api/v5/users/dodders/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/dodders/received_events",
                "type" : "User",
                "blog" : null,
                "weibo" : null,
                "bio" : "",
                "public_repos" : 11,
                "public_gists" : 0,
                "followers" : 0,
                "following" : 2,
                "stared" : 7,
                "watched" : 93,
                "created_at" : "2020-03-07T17:29:46+08:00",
                "updated_at" : "2022-11-09T11:03:12+08:00",
                "company" : null,
                "profession" : null,
                "wechat" : null,
                "qq" : null,
                "linkedin" : null,
                "email" : null,
                "organizations" : [ ]
            },
            "assignees_data" : [ ],
            "comments_data" : [  //issue评论
                {
                "id" : 14312838,  //评论id
                "body" : "Hey ***@dodders***, Welcome to openGauss Community.",  //评论body
                "user" : {  //评论用户信息
                    "id" : 5622128,
                    "login" : "opengauss-bot",
                    "name" : "opengauss-bot",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/1874/5622128_opengauss-bot_1581905080.png",
                    "url" : "https://gitee.com/api/v5/users/opengauss-bot",
                    "html_url" : "https://gitee.com/opengauss-bot",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/opengauss-bot/followers",
                    "following_url" : "https://gitee.com/api/v5/users/opengauss-bot/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/opengauss-bot/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/opengauss-bot/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/opengauss-bot/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/opengauss-bot/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/opengauss-bot/repos",
                    "events_url" : "https://gitee.com/api/v5/users/opengauss-bot/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/opengauss-bot/received_events",
                    "type" : "User"
                },
                "source" : null,  //web,api
                "target" : {  //评价目标
                    "issue" : {
                    "id" : 10108112,
                    "title" : "copy 指令帮助信息与文档不一致",
                    "number" : "I60NGW"
                    },
                    "pull_request" : null
                },
                "created_at" : "2022-11-11T11:42:46+08:00",  //评论创建时间
                "updated_at" : "2022-11-11T11:42:46+08:00",  //评论更新时间
                "user_data" : {  //评论用户信息
                    "id" : 5622128,
                    "login" : "opengauss-bot",
                    "name" : "opengauss-bot",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/1874/5622128_opengauss-bot_1581905080.png",
                    "url" : "https://gitee.com/api/v5/users/opengauss-bot",
                    "html_url" : "https://gitee.com/opengauss-bot",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/opengauss-bot/followers",
                    "following_url" : "https://gitee.com/api/v5/users/opengauss-bot/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/opengauss-bot/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/opengauss-bot/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/opengauss-bot/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/opengauss-bot/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/opengauss-bot/repos",
                    "events_url" : "https://gitee.com/api/v5/users/opengauss-bot/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/opengauss-bot/received_events",
                    "type" : "User",
                    "blog" : null,
                    "weibo" : null,
                    "bio" : null,
                    "public_repos" : 38,
                    "public_gists" : 0,
                    "followers" : 32,
                    "following" : 1,
                    "stared" : 9,
                    "watched" : 39,
                    "created_at" : "2020-01-09T18:19:46+08:00",
                    "updated_at" : "2022-11-15T15:06:01+08:00",
                    "company" : null,
                    "profession" : null,
                    "wechat" : null,
                    "qq" : null,
                    "linkedin" : null,
                    "email" : null,
                    "organizations" : [
                    {
                        "id" : 5549555,
                        "login" : "opengauss",
                        "name" : "openGauss",
                        "url" : "https://gitee.com/api/v5/orgs/opengauss",
                        "avatar_url" : "https://portrait.gitee.com/uploads/avatars/namespace/1849/5549555_opengauss_1581904918.png?is_link=true",
                        "repos_url" : "https://gitee.com/api/v5/orgs/opengauss/repos",
                        "events_url" : "https://gitee.com/api/v5/orgs/opengauss/events",
                        "members_url" : "https://gitee.com/api/v5/orgs/opengauss/members{/member}",
                        "description" : "一款高性能、高安全、高可靠的企业级开源关系型数据库。",
                        "follow_count" : 1095
                    }
                    ]
                }
                }  
            ]
        },
        "metadata__updated_on" : "2022-11-16T09:06:59+00:00",  //数据更新时间
        "metadata__timestamp" : "2022-11-16T09:30:41.604659+00:00"  //数据收集时间
    }
}



```
# pr data

index : gitee-pulls_raw, github-pulls_raw

```
{
    "_index" : "gitee-pulls_raw",  //index名称
    "_id" : "25d9276042074629b6bc8b46e7d18aecc52bc42f",  //id
    "_score" : 1.1650649,  //文档的相关性得分
    "_source" : {
        "backend_name" : "Gitee",  //backend名称(Git, Gitee, Github)
        "backend_version" : "0.1.0",   //backend版本
        "perceval_version" : "0.17.16",  //perceval版本
        "timestamp" : 1.659965419506045E9,  //raw数据收集时间戳(对应metadata__timestamp)
        "origin" : "https://gitee.com/mindspore/mindspore", //仓库地址
        "uuid" : "25d9276042074629b6bc8b46e7d18aecc52bc42f",  //uuid
        "updated_on" : 1.629792492E9,  //数据更新的时间戳(对应metadata__updated_on)
        "classified_fields_filtered" : null,  //过滤分类字段
        "category" : "pull_request",   //分类(commit, repository, issue, pull_request)
        "search_fields" : {  
            "item_id" : "4483990",
            "owner" : "mindspore",
            "repo" : "mindspore"
        },  //搜索字段信息
        "tag" : "https://gitee.com/mindspore/mindspore",  //仓库地址(跟origin一样)
        "data" : {
            "id" : 4483990,  //PRid
            "url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242",  //获取PR数据url
            "html_url" : "https://gitee.com/mindspore/mindspore/pulls/22242",  //获取PRhtml页面url
            "diff_url" : "https://gitee.com/mindspore/mindspore/pulls/22242.diff",  //获取PR commit文件变化url
            "patch_url" : "https://gitee.com/mindspore/mindspore/pulls/22242.patch", //获取PR commit文件变化url
            "issue_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/issues",  //获取关联的issue信息url
            "commits_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/commits",  //获取commit信息url
            "review_comments_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/comments/{/number}",  //获取review请求url
            "review_comment_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/comments",  //获取review请求url
            "comments_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/comments",   //获取PR全部comment信息
            "number" : 22242,  //PR 编号
            "state" : "merged",  //状态  open:打开 closed:关闭 merged:合并
            "assignees_number" : 0,  //代码审查人数
            "testers_number" : 0,  //代码测试人数
            "assignees" : [ ],  //代码审查用户信息
            "testers" : [ ],  //代码测试用户信息
            "milestone" : null,  //关联的里程碑
            "labels" : [
                {
                "id" : 50828636,
                "color" : "20c22e",
                "name" : "approved",
                "repository_id" : 5439905,
                "url" : "https://gitee.com/api/v5/enterprises/mind_spore/labels/approved",
                "created_at" : "2019-12-03T19:55:42+08:00",
                "updated_at" : "2022-08-08T21:14:53+08:00"
                }
            ],  //标签
            "locked" : false,  //是否已锁
            "created_at" : "2021-08-23T16:30:42+08:00",  //pr 创建时间
            "updated_at" : "2021-08-24T16:08:12+08:00",  //pr更新时间
            "closed_at" : "2021-08-24T16:08:12+08:00",  //pr 关闭时间
            "draft" : false,  //是否草稿
            "merged_at" : "2021-08-24T16:08:12+08:00",  //pr合并时间
            "mergeable" : true,  //是否可以合并
            "can_merge_check" : false,  //是否可以合并检查
            "_links" : {  //PR相关链接
                "self" : {
                "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242"
                },
                "html" : {
                "href" : "https://gitee.com/mindspore/mindspore/pulls/22242"
                },
                "issue" : {
                "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/issues"
                },
                "comments" : {
                "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/comments"
                },
                "review_comments" : {
                "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/comments"
                },
                "review_comment" : {
                "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/comments/22242"
                },
                "commits" : {
                "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242/commits"
                }
            },
            "user" : {
                "id" : 6579593,
                "login" : "yuximiao",
                "name" : "yuximiao",
                "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                "url" : "https://gitee.com/api/v5/users/yuximiao",
                "html_url" : "https://gitee.com/yuximiao",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/yuximiao/followers",
                "following_url" : "https://gitee.com/api/v5/users/yuximiao/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/yuximiao/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/yuximiao/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/yuximiao/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/yuximiao/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/yuximiao/repos",
                "events_url" : "https://gitee.com/api/v5/users/yuximiao/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/yuximiao/received_events",
                "type" : "User"
            },  //提交PR的用户信息
            "title" : "Fix code check.",  // pr 标题
            "body" : "What type of PR is this?",  //PR body
            "head" : {   //源分支信息
                "label" : "yuximiao_r1.3",
                "ref" : "yuximiao_r1.3",
                "sha" : "e6d5f55b87588339958c68fe185ad89fd23deea6",
                "user" : {
                "id" : 6579593,
                "login" : "yuximiao",
                "name" : "yuximiao",
                "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                "url" : "https://gitee.com/api/v5/users/yuximiao",
                "html_url" : "https://gitee.com/yuximiao",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/yuximiao/followers",
                "following_url" : "https://gitee.com/api/v5/users/yuximiao/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/yuximiao/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/yuximiao/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/yuximiao/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/yuximiao/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/yuximiao/repos",
                "events_url" : "https://gitee.com/api/v5/users/yuximiao/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/yuximiao/received_events",
                "type" : "User"
                },
                "repo" : { 
                "id" : 10300376,
                "full_name" : "yuximiao/mindspore",
                "human_name" : "yuximiao/mindspore",
                "url" : "https://gitee.com/api/v5/repos/yuximiao/mindspore",
                "namespace" : {
                    "id" : 5839982,
                    "type" : "personal",
                    "name" : "yuximiao",
                    "path" : "yuximiao",
                    "html_url" : "https://gitee.com/yuximiao"
                },
                "path" : "mindspore",
                "name" : "mindspore",
                "owner" : {
                    "id" : 6579593,
                    "login" : "yuximiao",
                    "name" : "yuximiao",
                    "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                    "url" : "https://gitee.com/api/v5/users/yuximiao",
                    "html_url" : "https://gitee.com/yuximiao",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/yuximiao/followers",
                    "following_url" : "https://gitee.com/api/v5/users/yuximiao/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/yuximiao/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/yuximiao/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/yuximiao/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/yuximiao/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/yuximiao/repos",
                    "events_url" : "https://gitee.com/api/v5/users/yuximiao/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/yuximiao/received_events",
                    "type" : "User"
                },
                "assigner" : {
                    "id" : 6579593,
                    "login" : "yuximiao",
                    "name" : "yuximiao",
                    "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                    "url" : "https://gitee.com/api/v5/users/yuximiao",
                    "html_url" : "https://gitee.com/yuximiao",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/yuximiao/followers",
                    "following_url" : "https://gitee.com/api/v5/users/yuximiao/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/yuximiao/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/yuximiao/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/yuximiao/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/yuximiao/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/yuximiao/repos",
                    "events_url" : "https://gitee.com/api/v5/users/yuximiao/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/yuximiao/received_events",
                    "type" : "User"
                },
                "description" : "MindSpore is a new open source deep learning training/inference framework that could be used for mobile, edge and cloud scenarios.",
                "private" : false,
                "public" : true,
                "internal" : false,
                "fork" : true,
                "html_url" : "https://gitee.com/yuximiao/mindspore.git",
                "ssh_url" : "git@gitee.com:yuximiao/mindspore.git"
                }
            },
            "base" : {   //目标分支信息
                "label" : "r1.3",
                "ref" : "r1.3",
                "sha" : "273330f59dee8cfcc5921839ddc34fa915bbaed3",
                "user" : {
                "id" : 5625371,
                "login" : "iambowen1984",
                "name" : "iambowen1984",
                "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                "url" : "https://gitee.com/api/v5/users/iambowen1984",
                "html_url" : "https://gitee.com/iambowen1984",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/iambowen1984/followers",
                "following_url" : "https://gitee.com/api/v5/users/iambowen1984/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/iambowen1984/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/iambowen1984/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/iambowen1984/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/iambowen1984/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/iambowen1984/repos",
                "events_url" : "https://gitee.com/api/v5/users/iambowen1984/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/iambowen1984/received_events",
                "type" : "User"
                },
                "repo" : {
                "id" : 8649239,
                "full_name" : "mindspore/mindspore",
                "human_name" : "MindSpore/mindspore",
                "url" : "https://gitee.com/api/v5/repos/mindspore/mindspore",
                "namespace" : {
                    "id" : 6854763,
                    "type" : "group",
                    "name" : "MindSpore",
                    "path" : "mindspore",
                    "html_url" : "https://gitee.com/mindspore"
                },
                "path" : "mindspore",
                "name" : "mindspore",
                "owner" : {
                    "id" : 6560119,
                    "login" : "zhunaipan",
                    "name" : "zhunaipan",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/2186/6560119_panza_1584156773.png",
                    "url" : "https://gitee.com/api/v5/users/zhunaipan",
                    "html_url" : "https://gitee.com/zhunaipan",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/zhunaipan/followers",
                    "following_url" : "https://gitee.com/api/v5/users/zhunaipan/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/zhunaipan/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/zhunaipan/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/zhunaipan/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/zhunaipan/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/zhunaipan/repos",
                    "events_url" : "https://gitee.com/api/v5/users/zhunaipan/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/zhunaipan/received_events",
                    "type" : "User"
                },
                "assigner" : {
                    "id" : 5625371,
                    "login" : "iambowen1984",
                    "name" : "iambowen1984",
                    "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                    "url" : "https://gitee.com/api/v5/users/iambowen1984",
                    "html_url" : "https://gitee.com/iambowen1984",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/iambowen1984/followers",
                    "following_url" : "https://gitee.com/api/v5/users/iambowen1984/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/iambowen1984/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/iambowen1984/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/iambowen1984/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/iambowen1984/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/iambowen1984/repos",
                    "events_url" : "https://gitee.com/api/v5/users/iambowen1984/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/iambowen1984/received_events",
                    "type" : "User"
                },
                "description" : "MindSpore is a new open source deep learning training/inference framework that could be used for mobile, edge and cloud scenarios.",
                "private" : false,
                "public" : true,
                "internal" : false,
                "fork" : false,
                "html_url" : "https://gitee.com/mindspore/mindspore.git",
                "ssh_url" : "git@gitee.com:mindspore/mindspore.git"
                }
            },
            "user_data" : {  //提交PR的用户信息(更详细)
                "id" : 6579593,
                "login" : "yuximiao",
                "name" : "yuximiao",
                "avatar_url" : "https://gitee.com/assets/no_portrait.png",
                "url" : "https://gitee.com/api/v5/users/yuximiao",
                "html_url" : "https://gitee.com/yuximiao",
                "remark" : "",
                "followers_url" : "https://gitee.com/api/v5/users/yuximiao/followers",
                "following_url" : "https://gitee.com/api/v5/users/yuximiao/following_url{/other_user}",
                "gists_url" : "https://gitee.com/api/v5/users/yuximiao/gists{/gist_id}",
                "starred_url" : "https://gitee.com/api/v5/users/yuximiao/starred{/owner}{/repo}",
                "subscriptions_url" : "https://gitee.com/api/v5/users/yuximiao/subscriptions",
                "organizations_url" : "https://gitee.com/api/v5/users/yuximiao/orgs",
                "repos_url" : "https://gitee.com/api/v5/users/yuximiao/repos",
                "events_url" : "https://gitee.com/api/v5/users/yuximiao/events{/privacy}",
                "received_events_url" : "https://gitee.com/api/v5/users/yuximiao/received_events",
                "type" : "User",
                "blog" : null,
                "weibo" : null,
                "bio" : null,
                "public_repos" : 6,
                "public_gists" : 0,
                "followers" : 0,
                "following" : 2,
                "stared" : 2,
                "watched" : 8,
                "created_at" : "2020-03-18T16:54:31+08:00",
                "updated_at" : "2022-07-27T08:34:02+08:00",
                "company" : null,
                "profession" : null,
                "wechat" : null,
                "qq" : null,
                "linkedin" : null,
                "email" : null,
                "organizations" : [
                {
                    "id" : 6854763,
                    "login" : "mindspore",
                    "name" : "MindSpore",
                    "url" : "https://gitee.com/api/v5/orgs/mindspore",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/namespace/2284/6854763_mindspore_1604325217.png?is_link=true",
                    "repos_url" : "https://gitee.com/api/v5/orgs/mindspore/repos",
                    "events_url" : "https://gitee.com/api/v5/orgs/mindspore/events",
                    "members_url" : "https://gitee.com/api/v5/orgs/mindspore/members{/member}",
                    "description" : "Open Source deep learning training/inference framework that could be used for mobile, edge and cloud scenarios.",
                    "follow_count" : 1680
                }
                ]
            },
            "review_comments_data" : [  //PR的评论列表数据
                {
                "url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/comments/6360832",   //获取pr评论信息
                "id" : 6360832,  //评论id
                "path" : null,
                "position" : null,
                "original_position" : null,
                "new_line" : null,
                "commit_id" : null,
                "original_commit_id" : null,
                "user" : {  //评论用户信息
                    "id" : 8777557,
                    "login" : "test-bot",
                    "name" : "mindspore-dx-bot",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/2925/8777557_test-bot_1617846881.png",
                    "url" : "https://gitee.com/api/v5/users/test-bot",
                    "html_url" : "https://gitee.com/test-bot",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/test-bot/followers",
                    "following_url" : "https://gitee.com/api/v5/users/test-bot/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/test-bot/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/test-bot/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/test-bot/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/test-bot/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/test-bot/repos",
                    "events_url" : "https://gitee.com/api/v5/users/test-bot/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/test-bot/received_events",
                    "type" : "User"
                },
                "created_at" : "2021-08-23T16:30:44+08:00",  //评论创建时间
                "updated_at" : "2021-08-23T16:30:44+08:00",  //评论更新时间
                "body" : "Please add labels (comp or sig),also you can visit",  //评论body
                "html_url" : "https://gitee.com/mindspore/mindspore/pulls/22242#note_6360832",  //获取评论的html_url
                "pull_request_url" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242", //获取PR信息url
                "_links" : { //链接
                    "self" : {
                    "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/comments/6360832"
                    },
                    "html" : {
                    "href" : "https://gitee.com/mindspore/mindspore/pulls/22242#note_6360832_conversation_15154165"
                    },
                    "pull_request" : {
                    "href" : "https://gitee.com/api/v5/repos/mindspore/mindspore/pulls/22242"
                    }
                },
                "comment_type" : "pr_comment", //评论类型 diff_comment:代码行评论  pr_comment:pr普通评论
                "user_data" : {  //评论用户信息
                    "id" : 8777557,
                    "login" : "test-bot",
                    "name" : "mindspore-dx-bot",
                    "avatar_url" : "https://portrait.gitee.com/uploads/avatars/user/2925/8777557_test-bot_1617846881.png",
                    "url" : "https://gitee.com/api/v5/users/test-bot",
                    "html_url" : "https://gitee.com/test-bot",
                    "remark" : "",
                    "followers_url" : "https://gitee.com/api/v5/users/test-bot/followers",
                    "following_url" : "https://gitee.com/api/v5/users/test-bot/following_url{/other_user}",
                    "gists_url" : "https://gitee.com/api/v5/users/test-bot/gists{/gist_id}",
                    "starred_url" : "https://gitee.com/api/v5/users/test-bot/starred{/owner}{/repo}",
                    "subscriptions_url" : "https://gitee.com/api/v5/users/test-bot/subscriptions",
                    "organizations_url" : "https://gitee.com/api/v5/users/test-bot/orgs",
                    "repos_url" : "https://gitee.com/api/v5/users/test-bot/repos",
                    "events_url" : "https://gitee.com/api/v5/users/test-bot/events{/privacy}",
                    "received_events_url" : "https://gitee.com/api/v5/users/test-bot/received_events",
                    "type" : "User",
                    "blog" : null,
                    "weibo" : null,
                    "bio" : "",
                    "public_repos" : 1,
                    "public_gists" : 0,
                    "followers" : 2,
                    "following" : 3,
                    "stared" : 0,
                    "watched" : 2,
                    "created_at" : "2021-03-09T15:15:12+08:00",
                    "updated_at" : "2021-10-25T16:47:31+08:00",
                    "company" : null,
                    "profession" : null,
                    "wechat" : null,
                    "qq" : null,
                    "linkedin" : null,
                    "email" : null,
                    "organizations" : [
                    {
                        "id" : 7051233,
                        "login" : "meta-oss",
                        "name" : "Meta-OSS",
                        "url" : "https://gitee.com/api/v5/orgs/meta-oss",
                        "avatar_url" : "no_portrait.png#Meta-OSS-meta-oss",
                        "repos_url" : "https://gitee.com/api/v5/orgs/meta-oss/repos",
                        "events_url" : "https://gitee.com/api/v5/orgs/meta-oss/events",
                        "members_url" : "https://gitee.com/api/v5/orgs/meta-oss/members{/member}",
                        "description" : "从事开源已三载，分享一些开源的元工具、元模型、元数据...",
                        "follow_count" : 3
                    }
                    ]
                }
                }
            ],
            "reviews_data" : [ ],  
            "merged_by_data" : [ ],  //merge用户信息
            "commits_data" : [  //commits id
                "e6d5f55b87588339958c68fe185ad89fd23deea6"
            ],
            "merged_by" : null,   //merge用户名
            "linked_issues" : [  //关联issues的链接
                "https://gitee.com/mindspore/mindspore/issues/I41SZN"
            ]
        },
        "metadata__updated_on" : "2021-08-24T08:08:12+00:00",  //数据更新时间
        "metadata__timestamp" : "2022-08-08T13:30:19.506045+00:00"  //raw数据收集时的时间
    }
}
```
# Enrich Data
# git data

index : gitee-git_enriched, github-git_enriched

```
{
  "_index" : "gitee-git_enriched",   //index名称
  "_id" : "bb6658ca89bdb1109d125b2d2b73051ea469bf50",  //id
  "_score" : 1.0,  //文档的相关性得分
  "_source" : {
    "metadata__updated_on" : "2022-07-28T03:18:47+00:00",  //数据更新时间
    "metadata__timestamp" : "2022-09-20T14:59:34.201459+00:00",  //raw数据收集时的时间
    "offset" : null,
    "origin" : "https://gitee.com/lishengbao/python_test.git",  //仓库地址
    "tag" : "https://gitee.com/lishengbao/python_test.git", //仓库地址
    "uuid" : "bb6658ca89bdb1109d125b2d2b73051ea469bf50",   //uuid
    "git_uuid" : "bb6658ca89bdb1109d125b2d2b73051ea469bf50", //git uuid
    "message" : "Initial commit", //commit描述
    "hash" : "cd3523665deeac1fe7833d9d761b4167ae369129", //commit hash
    "message_analyzed" : "Initial commit",   //commit描述分析
    "commit_tags" : [ ],
    "hash_short" : "cd3523",  //commit hash(简写)
    "author_date" : "2022-07-28T03:18:47", //作者时间
    "commit_date" : "2022-07-28T03:18:47", //commit提交时间
    "author_date_weekday" : 4,  //作者对应星期几 1-7:对应星期一到星期天
    "author_date_hour" : 3, //作者对应小时
    "commit_date_weekday" : 4,   //commit对应星期几 1-7:对应星期一到星期天
    "commit_date_hour" : 3, //commit对应小时
    "utc_author" : "2022-07-28T03:18:47",  //作者时间(0时区)
    "utc_commit" : "2022-07-28T03:18:47",  //commit提交时间(0时区)
    "utc_author_date_weekday" : 4,  //作者对应星期几(0时区)
    "utc_author_date_hour" : 3, //作者对应小时(0时区)
    "utc_commit_date_weekday" : 4, //commit对应星期几(0时区)
    "utc_commit_date_hour" : 3,  //commit对应小时(0时区)
    "tz" : 0, //当前时区
    "branches" : [ ], //分支
    "time_to_commit_hours" : 0.0, //时间差=编写时间-commit时间(单位:小时)
    "repo_name" : "https://gitee.com/lishengbao/python_test.git", //仓库地址
    "files" : 2,    //文件变化总数
    "lines_added" : 75,  //文件新增总行数
    "lines_removed" : 0, //文件减少总行数
    "lines_changed" : 75, //文件变化总行数
    "author_name" : "lishengbao",  //作者名称
    "author_domain" : "qq.com",  //作者域名
    "committer_name" : "Gitee",  //提交者名称
    "committer_domain" : "gitee.com",  //提交者域名
    "title" : "Initial commit",  //提交描述
    "git_author_domain" : "qq.com",  
    "grimoire_creation_date" : "2022-07-28T03:18:47+00:00",  //数据创建时间(对应metadata__updated_on)
    "is_git_commit" : 1,  //是否git commit
    "Author_id" : "639bb38af6369cf2edc31d5f448081c64603328d",  //作者id(在MariaDB中保存的数据)
    "Author_uuid" : "639bb38af6369cf2edc31d5f448081c64603328d",  //作者uuid(在MariaDB中保存的数据)
    "Author_name" : "lishengbao",  //作者名称(在MariaDB中保存的数据)
    "Author_user_name" : "Unknown",  //作者用户名称
    "Author_domain" : "qq.com",  //作者域名
    "Author_gender" : "Unknown",  //作者性别
    "Author_gender_acc" : 0,
    "Author_org_name" : "Unknown",  //作者组织名称
    "Author_bot" : false,  //作者是否机器人
    "Author_multi_org_names" : [  
      "Unknown" 
    ],  //作者多个组织名称
    "Commit_id" : "c755d0cbb1d1294e5920a5eca86b9dee0f470f72",  //提交者id(在MariaDB中保存的数据)
    "Commit_uuid" : "c755d0cbb1d1294e5920a5eca86b9dee0f470f72",  //提交者uuid(在MariaDB中保存的数据)
    "Commit_name" : "Gitee",  //提交者名称(在MariaDB中保存的数据)
    "Commit_user_name" : "Unknown",  //提交者用户名称
    "Commit_domain" : "gitee.com",  //提交者域名
    "Commit_gender" : "Unknown",  //提交者性别
    "Commit_gender_acc" : 0,
    "Commit_org_name" : "Unknown",  //提交者组织名称
    "Commit_bot" : false,  //提交者是否机器人
    "Commit_multi_org_names" : [
      "Unknown"
    ],  //提交者多个组织名称
    "author_id" : "639bb38af6369cf2edc31d5f448081c64603328d",
    "author_uuid" : "639bb38af6369cf2edc31d5f448081c64603328d",
    "author_user_name" : "Unknown",
    "author_gender" : "Unknown",
    "author_gender_acc" : 0,
    "author_org_name" : "Unknown",
    "author_bot" : false,
    "author_multi_org_names" : [
      "Unknown"
    ],
    "project" : "gitee-python_test", //gitee-仓库名
    "project_1" : "gitee-python_test", //gitee-仓库名
    "repository_labels" : [ ],
    "metadata__filter_raw" : null,
    "acked_by_multi_bots" : [ ],
    "acked_by_multi_domains" : [ ],
    "acked_by_multi_names" : [ ],
    "acked_by_multi_org_names" : [ ],
    "acked_by_multi_uuids" : [ ],
    "co_developed_by_multi_bots" : [ ],
    "co_developed_by_multi_domains" : [ ],
    "co_developed_by_multi_names" : [ ],
    "co_developed_by_multi_org_names" : [ ],
    "co_developed_by_multi_uuids" : [ ],
    "reported_by_multi_bots" : [ ],
    "reported_by_multi_domains" : [ ],
    "reported_by_multi_names" : [ ],
    "reported_by_multi_org_names" : [ ],
    "reported_by_multi_uuids" : [ ],
    "reviewed_by_multi_bots" : [ ],
    "reviewed_by_multi_domains" : [ ],
    "reviewed_by_multi_names" : [ ],
    "reviewed_by_multi_org_names" : [ ],
    "reviewed_by_multi_uuids" : [ ],
    "signed_off_by_multi_bots" : [ ],
    "signed_off_by_multi_domains" : [ ],
    "signed_off_by_multi_names" : [ ],
    "signed_off_by_multi_org_names" : [ ],
    "signed_off_by_multi_uuids" : [ ],
    "suggested_by_multi_bots" : [ ],
    "suggested_by_multi_domains" : [ ],
    "suggested_by_multi_names" : [ ],
    "suggested_by_multi_org_names" : [ ],
    "suggested_by_multi_uuids" : [ ],
    "tested_by_multi_bots" : [ ],
    "tested_by_multi_domains" : [ ],
    "tested_by_multi_names" : [ ],
    "tested_by_multi_org_names" : [ ],
    "tested_by_multi_uuids" : [ ],
    "non_authored_acked_by_multi_bots" : [ ],
    "non_authored_acked_by_multi_domains" : [ ],
    "non_authored_acked_by_multi_names" : [ ],
    "non_authored_acked_by_multi_org_names" : [ ],
    "non_authored_acked_by_multi_uuids" : [ ],
    "non_authored_co_developed_by_multi_bots" : [ ],
    "non_authored_co_developed_by_multi_domains" : [ ],
    "non_authored_co_developed_by_multi_names" : [ ],
    "non_authored_co_developed_by_multi_org_names" : [ ],
    "non_authored_co_developed_by_multi_uuids" : [ ],
    "non_authored_reported_by_multi_bots" : [ ],
    "non_authored_reported_by_multi_domains" : [ ],
    "non_authored_reported_by_multi_names" : [ ],
    "non_authored_reported_by_multi_org_names" : [ ],
    "non_authored_reported_by_multi_uuids" : [ ],
    "non_authored_reviewed_by_multi_bots" : [ ],
    "non_authored_reviewed_by_multi_domains" : [ ],
    "non_authored_reviewed_by_multi_names" : [ ],
    "non_authored_reviewed_by_multi_org_names" : [ ],
    "non_authored_reviewed_by_multi_uuids" : [ ],
    "non_authored_signed_off_by_multi_bots" : [ ],
    "non_authored_signed_off_by_multi_domains" : [ ],
    "non_authored_signed_off_by_multi_names" : [ ],
    "non_authored_signed_off_by_multi_org_names" : [ ],
    "non_authored_signed_off_by_multi_uuids" : [ ],
    "non_authored_suggested_by_multi_bots" : [ ],
    "non_authored_suggested_by_multi_domains" : [ ],
    "non_authored_suggested_by_multi_names" : [ ],
    "non_authored_suggested_by_multi_org_names" : [ ],
    "non_authored_suggested_by_multi_uuids" : [ ],
    "non_authored_tested_by_multi_bots" : [ ],
    "non_authored_tested_by_multi_domains" : [ ],
    "non_authored_tested_by_multi_names" : [ ],
    "non_authored_tested_by_multi_org_names" : [ ],
    "non_authored_tested_by_multi_uuids" : [ ],
    "metadata__gelk_version" : "0.103.0-rc.4", //elk版本
    "metadata__gelk_backend_name" : "GitEnrich", //elk backend名称
    "metadata__enriched_on" : "2022-10-11T03:28:02.927319+00:00" //enrich处理时间
  }
}
```
# repo data

index : gitee-repo_enriched, github-repo_enriched

```
{
    "_index" : "gitee-repo_enriched",  //index名称
    "_id" : "258d5cf635e3f38c5699161cb4ff9904f4db4d7f",  //id
    "_score" : 6.1369123,  //文档的相关性得分
    "_source" : {
      "metadata__updated_on" : "2022-09-14T15:36:04.302824+00:00",  //数据更新时间
      "metadata__timestamp" : "2022-09-14T15:36:04.302843+00:00",  //raw数据收集时的时间
      "offset" : null,
      "origin" : "https://gitee.com/mindspore/mindspore",  //仓库地址
      "tag" : "https://gitee.com/mindspore/mindspore",  //仓库地址
      "uuid" : "258d5cf635e3f38c5699161cb4ff9904f4db4d7f",  //uuid
      "forks_count" : 3189,  //仓库fork数量
      "subscribers_count" : 1873,   //仓库star数量
      "stargazers_count" : 6904,  //仓库watch数量
      "fetched_on" : 1.663169764302824E9,  //raw收集时间
      "url" : "https://gitee.com/mindspore/mindspore.git", //仓库地址
      "releases" : [
        {
          "id" : 62730,  //release id
          "tag_name" : "v0.1.0-alpha",  //release 名称
          "target_commitish" : "576a73b42a34a32b6bda6af262df1735a47d2e98",  //对应的commit
          "prerelease" : false,   //是否预发版本
          "name" : "v0.1.0-alpha",  //release 名称
          "body" : "# Release 0.1.0-alpha",    //release body
          "created_at" : "2020-03-27T21:13:11+08:00",   //创建时间
          "author" : {
            "login" : "zhunaipan",  //作者登录名称
            "name" : "zhunaipan"  //作者名称
          }
        }
      ],
      "releases_count" : 25,  //release数量
      "project" : "gitee-mindspore",  //gitee-仓库名
      "project_1" : "gitee-mindspore",  //gitee-仓库名
      "grimoire_creation_date" : "2022-09-14T15:36:04.302824+00:00",   //数据创建时间
      "is_gitee_repository" : 1,   //是否gitee仓库
      "repository_labels" : [ ],
      "metadata__filter_raw" : null,
      "metadata__gelk_version" : "0.103.0-rc.4",  //elk版本
      "metadata__gelk_backend_name" : "GiteeEnrich",  //elk backend名称
      "metadata__enriched_on" : "2022-11-01T07:20:29.713878+00:00"  //enrich处理时间
    }
}
```
# release data

index : gitee-releases_enriched, github-releases_enriched

```
{
    "_index" : "gitee-releases_enriched",  //index名称
    "_id" : "1a86c5b1fb357a77e2c75f884e8cfefe4a3f496f",  //id
    "_score" : 1.0,  //文档的相关性得分
    "_source" : {
        "uuid" : "1a86c5b1fb357a77e2c75f884e8cfefe4a3f496f",  //uuid
        "id" : 85656,   //release id
        "tag" : "https://gitee.com/openharmony/ability_ability_lite",  //仓库地址
        "tag_name" : "OpenHarmony-1.0",  //release 名称
        "target_commitish" : "7e34485f1d47eb8172ac3a100577a18a5b925da9",  //对应的commit
        "prerelease" : false,  //是否预发版本
        "name" : "OpenHarmony-1.0",   //release 名称
        "body" : "OpenHarmony-1.0",  //release body
        "author_login" : "wenjun_flyingfox",    //作者登录名称
        "author_name" : "wenjun",  //作者名称
        "grimoire_creation_date" : "2020-09-09T22:37:28+08:00"  //数据创建时间
    }
}
```
# issue data

index : gitee-issues_enriched, github-issues_enriched

```
{
    "_index" : "gitee-issues_enriched",  //index名称
    "_id" : "fc96ee418df32b4a4b2d23f8569152cccc60a7d3",  //id
    "_score" : null,  //文档的相关性得分
    "_source" : {
        "metadata__updated_on" : "2022-11-16T09:06:59+00:00",   //数据更新时间
        "metadata__timestamp" : "2022-11-16T09:30:41.604659+00:00",   //raw数据收集时的时间
        "offset" : null,
        "origin" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址
        "tag" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址
        "uuid" : "fc96ee418df32b4a4b2d23f8569152cccc60a7d3",  //uuid
        "time_to_close_days" : null,  //issue 打开到关闭的天数
        "time_open_days" : 5.9,  //PR 打开的天数
        "user_login" : "dodders",    //用户登录名
        "user_name" : "laishenghao",  //用户名
        "author_name" : "laishenghao",  //跟user_name一样
        "user_domain" : null,  //用户邮箱域名
        "user_org" : null,  //用户组织
        "user_location" : null,  //用户地址
        "user_geolocation" : null,  //用户定位
        "assignee_login" : "dodders",  //负责用户登录名
        "assignee_name" : "laishenghao",  //负责用户名
        "assignee_domain" : null,  //负责用户邮箱域名
        "assignee_org" : null,  //负责用户组织名
        "assignee_location" : null,  //负责用户地址
        "assignee_geolocation" : null,  //负责用户定位
        "id" : 10108112,  //issue id
        "id_in_repo" : "I60NGW",  //issue编号
        "repository" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址
        "title" : "copy 指令帮助信息与文档不一致",  //issue标题
        "title_analyzed" : "copy 指令帮助信息与文档不一致",  //issue标题
        "state" : "progressing",  //Issue的状态: open（开启的）, progressing(进行中), closed（关闭的）, rejected（拒绝的）
        "created_at" : "2022-11-11T11:42:33+08:00",  //issue创建时间
        "updated_at" : "2022-11-16T17:06:59+08:00",  //issue更新时间
        "closed_at" : null,   //issue 关闭时间
        "url" : "https://gitee.com/opengauss/openGauss-server/issues/I60NGW",  //获取PR html页面url
        "issue_type" : "缺陷",  //issue类型
        "labels" : [ ],  //标签名
        "pull_request" : false,  //是否是PR
        "item_type" : "issue",  //类型(issue, pull_request, comment, issue_comment, review_comment, repository)
        "gitee_repo" : "opengauss/openGauss-server",  //repo名
        "url_id" : "opengauss/openGauss-server/issues/I60NGW",  //url id
        "project" : "gitee-openGauss",  //gitee-仓库名
        "project_1" : "gitee-openGauss",  //gitee-仓库名
        "time_to_first_attention" : 0.0,  //comment第一次响应时间(从issue创建到第一次comment的时间,单位:天)
        "num_of_comments_without_bot" : 0,    //comment数量,排查机器人comment
        "time_to_first_attention_without_bot" : null,  //commet第一次响应时间(从issue创建到第一次comment的时间,排查机器人响应,单位:天)
        "grimoire_creation_date" : "2022-11-11T11:42:33+08:00",    //数据创建时间
        "is_gitee_issue" : 1,  //是否是gitee issue
        "assignee_data_id" : "2b8a58c719cd4c329ebc3867e294e2ab120aeafd",  //负责人id(在MariaDB中保存的数据)
        "assignee_data_uuid" : "2b8a58c719cd4c329ebc3867e294e2ab120aeafd",
        "assignee_data_name" : "laishenghao",
        "assignee_data_user_name" : "",
        "assignee_data_domain" : null,
        "assignee_data_gender" : "Unknown",
        "assignee_data_gender_acc" : 0,
        "assignee_data_org_name" : "Unknown",
        "assignee_data_bot" : false,
        "assignee_data_multi_org_names" : [
        "Unknown"
        ],
        "user_data_id" : "2b8a58c719cd4c329ebc3867e294e2ab120aeafd",  //用户id(在MariaDB中保存的数据)
        "user_data_uuid" : "2b8a58c719cd4c329ebc3867e294e2ab120aeafd",
        "user_data_name" : "laishenghao",
        "user_data_user_name" : "",
        "user_data_domain" : null,
        "user_data_gender" : "Unknown",
        "user_data_gender_acc" : 0,
        "user_data_org_name" : "Unknown",
        "user_data_bot" : false,
        "user_data_multi_org_names" : [
        "Unknown"
        ],
        "author_id" : "2b8a58c719cd4c329ebc3867e294e2ab120aeafd",  //作者id(在MariaDB中保存的数据)
        "author_uuid" : "2b8a58c719cd4c329ebc3867e294e2ab120aeafd",
        "author_user_name" : "",
        "author_domain" : null,
        "author_gender" : "Unknown",
        "author_gender_acc" : 0,
        "author_org_name" : "Unknown",
        "author_bot" : false,
        "author_multi_org_names" : [
        "Unknown"
        ],
        "repository_labels" : [ ],  //仓库标签
        "metadata__filter_raw" : null,
        "metadata__gelk_version" : "0.103.0-rc.4",  //elk版本
        "metadata__gelk_backend_name" : "GiteeEnrich",  //elk backend名称
        "metadata__enriched_on" : "2022-11-17T09:24:26.084429+00:00"  //enrich处理时间
    }
}



```
# issue comment data

index : gitee2-issues_enriched, github2-issues_enriched

```
{
    "_index" : "gitee2-issues_enriched",  //index名称
    "_id" : "10108112_issue_comment_14312838",  //id
    "_score" : null,  //文档的相关性得分
    "_source" : {
        "metadata__updated_on" : "2022-11-16T09:06:59+00:00",  //数据更新时间
        "metadata__timestamp" : "2022-11-16T09:30:41.714365+00:00",  //raw数据收集时的时间
        "offset" : null,
        "origin" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址
        "tag" : "https://gitee.com/opengauss/openGauss-server",  //仓库地址
        "uuid" : "fc96ee418df32b4a4b2d23f8569152cccc60a7d3",  //uuid
        "issue_labels" : [ ],  //issue 标签
        "issue_id" : 10108112,  //issue id
        "issue_id_in_repo" : "I60NGW",  //issue 编码
        "issue_url" : "https://gitee.com/opengauss/openGauss-server/issues/I60NGW",  //获取issue html页面url
        "issue_title" : "copy 指令帮助信息与文档不一致",  //issue 标题
        "issue_state" : "progressing",  //Issue的状态: open（开启的）, progressing(进行中), closed（关闭的）, rejected（拒绝的）
        "issue_created_at" : "2022-11-11T11:42:33+08:00",  //issue创建时间
        "issue_updated_at" : "2022-11-16T17:06:59+08:00",  //issue更新时间
        "issue_closed_at" : null,    //issue 关闭时间
        "issue_pull_request" : false,  //是否pr
        "gitee_repo" : "opengauss/openGauss-server", //仓库名称
        "repository" : "https://gitee.com/opengauss/openGauss-server",   //仓库地址
        "item_type" : "comment",  //类型(issue, pull_request, comment, issue_comment, review_comment, repository)
        "sub_type" : "issue_comment",   //子类型
        "body" : "Hey ***@dodders***, Welcome to openGauss Community.",  //comment body
        "body_analyzed" : "Hey ***@dodders***, Welcome to openGauss Community.",  //comment body
        "comment_updated_at" : "2022-11-11T11:42:46+08:00",  //评论更新时间
        "id" : "10108112_issue_comment_14312838",    //id  10108112:issue id   14312838:评论id
        "grimoire_creation_date" : "2022-11-11T11:42:46+08:00",    //数据创建时间
        "is_gitee_issue_comment" : 1,  //是否是gitee issue comment
        "is_gitee_comment" : 1,   //是否是gitee commet
        "user_login" : "opengauss-bot",  //用户登录账号
        "user_data_id" : "0a0129e9679f8bf65eed88a0d9205b610e0ad07f",  //用户id(在MariaDB中保存的数据)
        "user_data_uuid" : "0a0129e9679f8bf65eed88a0d9205b610e0ad07f",
        "user_data_name" : "opengauss-bot",
        "user_data_user_name" : "",
        "user_data_domain" : null,
        "user_data_gender" : "Unknown",
        "user_data_gender_acc" : 0,
        "user_data_org_name" : "Unknown",
        "user_data_bot" : false,
        "user_data_multi_org_names" : [
        "Unknown"
        ],
        "author_id" : "0a0129e9679f8bf65eed88a0d9205b610e0ad07f",  //作者id (在MariaDB中保存的数据)
        "author_uuid" : "0a0129e9679f8bf65eed88a0d9205b610e0ad07f",
        "author_name" : "opengauss-bot",
        "author_user_name" : "",
        "author_domain" : null,
        "author_gender" : "Unknown",
        "author_gender_acc" : 0,
        "author_org_name" : "Unknown",
        "author_bot" : false,
        "author_multi_org_names" : [
        "Unknown"
        ],
        "project" : "gitee-openGauss",  //gitee-仓库名
        "project_1" : "gitee-openGauss",  //gitee-仓库名
        "repository_labels" : [ ],
        "metadata__filter_raw" : null,
        "metadata__gelk_version" : "0.103.0-rc.4",  //elk版本
        "metadata__gelk_backend_name" : "GiteeEnrich2",   //elk backend名称
        "metadata__enriched_on" : "2022-11-17T09:31:46.242313+00:00"  //enrich处理时间
    }
}



```
# pr data

index : gitee-pulls_enriched, github-pulls_enriched

```
{
    "_index" : "gitee-pulls_enriched",  //index名称
    "_id" : "25d9276042074629b6bc8b46e7d18aecc52bc42f",  //id
    "_score" : 11.695013,  //文档的相关性得分
    "_source" : {
        "metadata__updated_on" : "2021-08-24T08:08:12+00:00",  //数据更新时间
        "metadata__timestamp" : "2022-08-08T13:30:19.506045+00:00",  //raw数据收集时的时间
        "offset" : null,
        "origin" : "https://gitee.com/mindspore/mindspore",  //仓库地址
        "tag" : "https://gitee.com/mindspore/mindspore",    //仓库地址
        "uuid" : "25d9276042074629b6bc8b46e7d18aecc52bc42f",  //uuid
        "time_to_close_days" : 0.98,   //PR 打开到关闭的天数
        "time_open_days" : 0.98,  //PR 打开的天数
        "user_login" : "yuximiao", //用户登录名
        "user_name" : "yuximiao",  //用户名
        "author_name" : "yuximiao",  //跟user_name一样
        "user_domain" : null,  //用户邮箱域名
        "user_org" : null,  //用户组织
        "user_location" : null,  //用户地址
        "user_geolocation" : null,  //用户地位
        "merge_author_name" : null,  //merge用户名
        "merge_author_login" : null,  //merge用户登录名
        "merge_author_domain" : null,  //merge用户邮箱域名
        "merge_author_org" : null,  //merge用户组织
        "merge_author_location" : null,  //merge用户地址
        "merge_author_geolocation" : null,  //merge定位
        "id" : 4483990,   //pr id
        "id_in_repo" : "22242",  // pr 编号
        "repository" : "https://gitee.com/mindspore/mindspore",  //仓库地址
        "title" : "Fix code check.",  //pr标题
        "title_analyzed" : "Fix code check.",  //pr标题
        "state" : "merged",    //状态  open:打开 closed:关闭 merged:合并
        "created_at" : "2021-08-23T16:30:42+08:00",  //pr 创建时间
        "updated_at" : "2021-08-24T16:08:12+08:00",  //pr更新时间
        "merged" : true,  //是否已合并
        "merged_at" : "2021-08-24T16:08:12+08:00",  //pr合并时间
        "closed_at" : "2021-08-24T16:08:12+08:00",   //pr 关闭时间
        "url" : "https://gitee.com/mindspore/mindspore/pulls/22242",  //获取PR html页面url
        "labels" : [  //标签名
            "approved",
            "lgtm",
            "mindspore-cla/yes",
            "ci-pipeline-passed"
        ],
        "pull_request" : true,  //是否是PR
        "item_type" : "pull request", //类型(issue, pull_request, comment, issue_comment, review_comment, repository)
        "gitee_repo" : "mindspore/mindspore",  //repo名
        "url_id" : "mindspore/mindspore/pull/22242", //url id
        "forks" : null,
        "code_merge_duration" : 0.98,  //PR 打开到合入的天数
        "num_review_comments" : 10,  //comment总数
        "time_to_merge_request_response" : 0.0,  //comment第一次响应时间(从pr创建到第一次review的时间,单位:天)
        "num_review_comments_without_bot" : 2,  //comment数量,排查机器人comment
        "time_to_first_attention_without_bot" : 0.8,  //commet第一次响应时间(从pr创建到第一次review的时间,排查机器人响应,单位:天)
        "linked_issues_count" : 1,  //关联issue数量
        "commits_data" : [  //关联的commit
        "e6d5f55b87588339958c68fe185ad89fd23deea6"
        ],
        "project" : "gitee-mindspore",  //gitee-仓库名
        "project_1" : "gitee-mindspore",  //gitee-仓库名
        "grimoire_creation_date" : "2021-08-23T16:30:42+08:00",  //数据创建时间
        "is_gitee_pull_request" : 1,  //是否是gitee pr
        "merged_by_data_id" : "",  //merge用户id(在MariaDB中保存的数据)
        "merged_by_data_uuid" : "",  //merge用户uuid(在MariaDB中保存的数据)
        "merged_by_data_name" : "Unknown",  //名称(在MariaDB中保存的数据)
        "merged_by_data_user_name" : "Unknown",  //用户名称
        "merged_by_data_domain" : "",  //域名
        "merged_by_data_gender" : "",  //性别
        "merged_by_data_gender_acc" : null,
        "merged_by_data_org_name" : "Unknown",  //组织名称
        "merged_by_data_bot" : false,  //是否机器人
        "merged_by_data_multi_org_names" : [
        ""
        ],  //多个组织名称
        "user_data_id" : "1a0d0c7e70531d8b28ed5fa5be6e834e3699d67d",  //用户id(在MariaDB中保存的数据)
        "user_data_uuid" : "1a0d0c7e70531d8b28ed5fa5be6e834e3699d67d",  //用户uuid(在MariaDB中保存的数据)
        "user_data_name" : "yuximiao",  //名称(在MariaDB中保存的数据)
        "user_data_user_name" : "",  //用户名称
        "user_data_domain" : null,  //域名
        "user_data_gender" : "Unknown",   //性别
        "user_data_gender_acc" : 0,
        "user_data_org_name" : "Unknown",  //组织名称
        "user_data_bot" : false,  //是否机器人
        "user_data_multi_org_names" : [
        "Unknown"
        ],   //多个组织名称
        "author_id" : "1a0d0c7e70531d8b28ed5fa5be6e834e3699d67d",
        "author_uuid" : "1a0d0c7e70531d8b28ed5fa5be6e834e3699d67d",
        "author_user_name" : "",
        "author_domain" : null,
        "author_gender" : "Unknown",
        "author_gender_acc" : 0,
        "author_org_name" : "Unknown",
        "author_bot" : false,
        "author_multi_org_names" : [
        "Unknown"
        ],
        "repository_labels" : [ ],  //仓库标签
        "metadata__filter_raw" : null,  
        "metadata__gelk_version" : "0.96.0",  //elk版本
        "metadata__gelk_backend_name" : "GiteeEnrich",   //elk backend名称
        "metadata__enriched_on" : "2022-08-13T05:00:36.018595+00:00"  //enrich处理时间
    }
}



```
# pr comment data

index : gitee2-pulls_enriched, github2-pulls_enriched

```
{
    "_index" : "gitee2-pulls_enriched",  //index名称
    "_id" : "4483990_review_comment_6360833",  //id 
    "_score" : 12.109089,   //文档的相关性得分
    "_source" : {
        "metadata__updated_on" : "2021-08-24T08:08:12+00:00",  //数据更新时间
        "metadata__timestamp" : "2022-07-26T04:41:10.697865+00:00",  //raw数据收集时的时间
        "offset" : null,
        "origin" : "https://gitee.com/mindspore/mindspore",  //仓库地址
        "tag" : "https://gitee.com/mindspore/mindspore",  //仓库地址
        "uuid" : "25d9276042074629b6bc8b46e7d18aecc52bc42f",  //uuid
        "review_state" : "",
        "pull_labels" : [
        "approved",
        "lgtm",
        "mindspore-cla/yes",
        "ci-pipeline-passed"
        ], //pr 标签名
        "pull_id" : 4483990,  //pr id
        "pull_id_in_repo" : "22242",  //pr编码
        "issue_id_in_repo" : "22242",  //pr编码
        "issue_title" : "Fix code check.",    //pr标题
        "issue_url" : "https://gitee.com/mindspore/mindspore/pulls/22242",  //获取PR html页面url
        "pull_url" : "https://gitee.com/mindspore/mindspore/pulls/22242",  //获取PR html页面url
        "pull_state" : "merged",  //PR状态  open:打开 closed:关闭 merged:合并
        "pull_created_at" : "2021-08-23T16:30:42+08:00",  //pr 创建时间
        "pull_updated_at" : "2021-08-24T16:08:12+08:00",  //pr更新时间
        "pull_merged_at" : "2021-08-24T16:08:12+08:00",  //pr合并时间
        "pull_closed_at" : "2021-08-24T16:08:12+08:00",  //pr 关闭时间
        "pull_merged" : true,  //是否已合并
        "gitee_repo" : "mindspore/mindspore",  //仓库名称
        "repository" : "https://gitee.com/mindspore/mindspore",  //仓库地址
        "item_type" : "comment",  //类型(issue, pull_request, comment, issue_comment, review_comment, repository)
        "sub_type" : "review_comment",  //子类型
        "body" : "***@yuximiao***, Thanks for your pull request. All the authors of commits have finished signinig CLA successfully. :wave: ",   //comment body
        "body_analyzed" : "***@yuximiao***, Thanks for your pull request. All the authors of commits have finished signinig CLA successfully. :wave: ",  //comment body
        "url" : "https://gitee.com/mindspore/mindspore/pulls/22242#note_6360833",  //获取评论信息
        "comment_updated_at" : "2021-08-23T16:30:44+08:00",  //评论更新时间
        "comment_created_at" : "2021-08-23T16:30:44+08:00",  //评论创建时间
        "id" : "4483990_review_comment_6360833",  //id  4483990:pr id    6360833:评论id
        "grimoire_creation_date" : "2021-08-23T16:30:44+08:00",  //数据创建时间
        "is_gitee_review_comment" : 1,  //是否是gitee review comment
        "is_gitee_comment" : 1,  //是否是gitee commet
        "user_login" : "I-am-a-robot",  //用户登录账号
        "user_data_id" : "fc63ab2e8cb184788339cdc26d1bb8caa6b4e98f",    //用户id(在MariaDB中保存的数据)
        "user_data_uuid" : "fc63ab2e8cb184788339cdc26d1bb8caa6b4e98f",
        "user_data_name" : "i-robot", //用户名称
        "user_data_user_name" : "",
        "user_data_domain" : null,
        "user_data_gender" : "Unknown",
        "user_data_gender_acc" : 0,
        "user_data_org_name" : "Unknown",
        "user_data_bot" : false,
        "user_data_multi_org_names" : [
        "Unknown"
        ],
        "author_id" : "fc63ab2e8cb184788339cdc26d1bb8caa6b4e98f",
        "author_uuid" : "fc63ab2e8cb184788339cdc26d1bb8caa6b4e98f",
        "author_name" : "i-robot",
        "author_user_name" : "",
        "author_domain" : null,
        "author_gender" : "Unknown",
        "author_gender_acc" : 0,
        "author_org_name" : "Unknown",
        "author_bot" : false,
        "author_multi_org_names" : [
        "Unknown"
        ],
        "project" : "gitee-mindspore",  //gitee-仓库名
        "project_1" : "gitee-mindspore",  //gitee-仓库名
        "repository_labels" : [ ],
        "metadata__filter_raw" : null,
        "metadata__gelk_version" : "0.101.1",  //elk版本
        "metadata__gelk_backend_name" : "GiteeEnrich2",  //elk backend名称
        "metadata__enriched_on" : "2022-08-04T04:06:41.126724+00:00"  //enrich处理时间
    }
}

```

# contributor data

index : gitee_contributors_org_repo, github_contributors_org_repo

```
{
    "_index" : "github_contributors_org_repo",   //index名称
    "_id" : "69aa8dc5589d6306de726ac0fe4cdc2dc1bf24c6",  //id 
    "_score" : 1.0,
    "_source" : {
      "uuid" : "69aa8dc5589d6306de726ac0fe4cdc2dc1bf24c6",   //id 
      "id_git_author_name_list" : [     //Git作者名称
        "Travis Beatty"
      ],    
      "id_git_author_email_list" : [   //Git 作者邮箱
        "travisby@gmail.com"
      ],  
      "id_platform_login_name_list" : [     // 平台(Github/Gitee)登录名称
        "travisby"
      ],  
      "id_platform_author_name_list" : [    // 平台(Github/Gitee)作者名称
        "Travis Beatty"
      ],   
      "id_platform_author_email_list" : [    // 平台(Github/Gitee)作者邮箱
        "travisby@gmail.com"         
      ],  
      "id_identity_list" : [       //贡献者身份信息(对贡献者邮箱前缀和贡献者名称去除特殊符号后, 并统一小写后得到)
        "travisby",
        "travisbeatty"
      ],
      "first_issue_creation_date" : "2014-06-11T12:21:55.014834+00:00",     //首次Issue创建时间
      "first_pr_creation_date" : "2014-06-11T12:21:55.014834+00:00",        //首次PR创建时间
      "first_issue_comments_date" : "2014-06-11T12:21:55.014834+00:00",     //首次Issue评论时间
      "first_pr_review_date" : "2014-06-11T12:21:55.014834+00:00",          //首次PR评论时间
      "first_code_commit_date" : "2014-06-11T08:21:45.083475+00:00",        //首次Code提交时间
      "first_fork_date" : "2014-06-11T12:16:06.082526+00:00",   //首次fork时间
      "first_star_date" : "2014-06-11T12:16:06.082526+00:00",   //首次star时间
      "first_watch_date" : "2014-06-11T12:16:06.082526+00:00",  //首次watch时间
      "issue_creation_date_list" : [                //Issue创建时间列表    
        "2014-06-11T12:16:06.082526+00:00",
        "2014-06-11T12:16:06.082526+00:00"
      ],
      "pr_creation_date_list" : [                   //PR创建时间列表
        "2014-06-11T12:21:55.014834+00:00"
      ],
      "issue_comments_date_list" : [                //Issue评论时间列表
        "2014-06-11T12:16:06.082526+00:00",
        "2014-06-11T12:16:06.082526+00:00"
      ],             
      "pr_review_date_list" : [                     //PR评论时间列表
        "2014-06-11T12:16:06.082526+00:00",
        "2014-06-11T12:16:06.082526+00:00"
      ],
      "code_commit_date_list" : [                   //Code提交时间列表
        "2014-06-11T08:21:45.083475+00:00"
      ],
      "fork_date_list" : [                          //fork时间列表
        "2014-06-11T12:16:06.082526+00:00"
      ],
      "star_date_list" : [                          //star时间列表
        "2014-06-11T12:16:06.082526+00:00"
      ],
      "watch_date_list" : [                         //watch时间列表
        "2014-06-11T12:16:06.082526+00:00"
      ],
      "last_contributor_date" : "2014-06-11T12:21:55.014834+00:00",         //最后贡献时间
      "org_change_date_list" : [                   //组织转变时间列表 
        {
          "domain" : "gmail.com",                               //邮箱后缀
          "org_name" : null,                                    //组织名
          "first_date" : "2014-06-11T08:21:45.083475+00:00",    //组织贡献开始时间
          "last_date" : "2014-06-11T08:21:45.083475+00:00"      //组织贡献结束时间
        }
      ],
      "platform_type" : "github",       //平台类(github / gitee)
      "domain" : "gmail.com",           //最后参与贡献的邮箱后缀
      "org_name" : null,                //最后参与贡献的组织名
      "community" : "kubernetes",       //社区名
      "repo_name" : "https://github.com/kubernetes/kubernetes",     //仓库名
      "is_bot" : false,                 //是否机器人
      "update_at_date" : "2023-07-13T05:09:35.908271+00:00"         //文档数据更新时间
    }
} 
```


# Model Data
# Activity-活跃度模型

index : compass_metric_model_activity

```
{
    "_index" : "compass_metric_model_activity",
    "_id" : "144e577a6cf94671b4fe67387ca8d9439623f2e1",
    "_score" : 4.5997477,
    "_source" : {
        "uuid" : "144e577a6cf94671b4fe67387ca8d9439623f2e1",  //uuid
        "level" : "repo",  //级别 repo:单仓  community:多仓
        "type" : null,  //类型  单仓时:null  多仓时(制品仓:software-artifact 治理仓:governance)
        "label" : "https://gitee.com/mindspore/mindspore",  //标签  单仓库时:具体仓库地址  多仓时:具体组织
        "model_name" : "Activity",  //模型名称
        "contributor_count" : 555,  //D1开发者数量 (过去90天活跃的开发者数量)  0:代表没有值
        "active_C2_contributor_count" : 285, //D2开发者数量 (过去90天活跃的开发者数量)  0:代表没有值
        "active_C1_pr_create_contributor" : 298,  //C1_PR创建者数量 (过去90天活跃的开发者数量)  0:代表没有值
        "active_C1_pr_comments_contributor" : 321,  //C1_PR评论者数量 (过去90天活跃的开发者数量)  0:代表没有值
        "active_C1_issue_create_contributor" : 235,  //C1_issue创建者数量 (过去90天活跃的开发者数量) 0:代表没有值
        "active_C1_issue_comments_contributor" : 134,  //C1_issue评论者数量 (过去90天活跃的开发者数量) 0:代表没有值
        "commit_frequency" : 463.03501945525295,  //平均提交次数 (过去90天每周提交的平均次数) 0:代表没有值
        "org_count" : 4,  //组织个数 (过去90天活跃的D2开发者所属组织个数) 0:代表没有值
        "created_since" : 10.48, //自创建以来时间 (自代码仓创建以来的时间（月）) 0:代表没有值
        "comment_frequency" : 0.618,  //issue评论平均数 (过去90天每个issue评论数的均值) 0:代表没有值 null:没有issue
        "code_review_count" : 3.4453, //pr评论平均数 (过去90天新建PR评论数的均值) 0:代表没有值 null:没有PR
        "updated_since" : 0.01,  //自更新以来时间 (最后一次Code Commit截至到统计时间的均值（月）)  0:代表没有值
        "closed_issues_count" : 904, //issue关闭数 (过去90天issue关闭的个数)  0:代表没有值
        "updated_issues_count" : 905, //issue更新数 (过去90天issue更新的个数)  0:代表没有值
        "recent_releases_count" : 10,  //release数 (过去一年发布版本的次数)  0:代表没有值
        "grimoire_creation_date" : "2021-02-01T00:00:00+00:00",  //数据统计时间
        "metadata__enriched_on" : "2022-11-21T06:45:45.178520+00:00",  //当时跑model的时间
        "activity_score" : 0.7471471552869109   //模型得分
    }
}
```
# Collaboration Development Index 协作开发指数 

（Code Quality Guarantee --->  Collaboration Development Index ）

index : compass_metric_model_codequality

```
{
    "_index" : "compass_metric_model_codequality",
    "_id" : "94e798aebf5860ae37489fcc902322b6884459f4",
    "_score" : null,
    "_source" : {
        "uuid" : "94e798aebf5860ae37489fcc902322b6884459f4",  //uuid
        "level" : "repo",  //级别 repo:单仓  community:多仓
        "type" : null,  //类型  单仓时:null  多仓时(制品仓:software-artifact 治理仓:governance)
        "label" : "https://gitee.com/mindspore/mindspore",  //标签  单仓库时:具体仓库地址  多仓时:具体组织
        "model_name" : "Code_Quality_Guarantee",  //模型名称
        "contributor_count" : 666,  //开发者数量 (过去90天活跃的PR creator, code reviewer 以及 code commit开发者数量)
        "active_C2_contributor_count" : 353,   //D2开发者数量
        "active_C1_pr_create_contributor" : 393, //C1_PR创建者数量
        "active_C1_pr_comments_contributor" : 416, //C1_PR评论者数量
        "commit_frequency" : 571.9066147859922,  //平均提交次数 (过去90天每周提交的平均次数)
        "commit_frequency_inside" : 534.7081712062256,  // 公司内部平均提交次数
        "is_maintained" : 1.0,  //提交周占比 (最近90天，至少有一次提交code的周占比)
        "LOC_frequency" : 64982.879377431906, //代码行数 (过去90天每周提交的代码行数的均值)
        "lines_added_frequency" : 39035.330739299614, //代码添加行数
        "lines_removed_frequency" : 25947.548638132295,  //代码删除行数
        "pr_issue_linked_ratio" : 0.42898490800082695,   //pr关联issue比例(过去90天新建pr关联issue的比例)
        "code_review_ratio" : 0.7899524498656192, //pr review比例 (最近90天新建PR至少有一个reviewer（非PR creator）的比例)
        "code_merge_ratio" : 0.9971783295711061, //pr merge比例 (最近90天新建并已合入的PR中，PR Merger与PR author不是同一个人的比例)
        "pr_count" : 4837, //pr 数量 (最近90天新建的PR数量)
        "pr_merged_count" : 3544, //pr merge 数量 (最近90天新建的PR中,合入数量)
        "pr_commit_count" : 3648, //commit 数量 (最近90天提交的数量)
        "pr_commit_linked_count" : 3094, // pr关联commit的数量 (过去90新建commit，通过pr提交的数量)
        "git_pr_linked_ratio" : 0.8481359649122807,  // pr关联commit的比例 (过去90新建commit，通过pr提交的比例)
        "grimoire_creation_date" : "2022-11-14T00:00:00+00:00",  //数据统计时间
        "metadata__enriched_on" : "2022-11-21T06:30:22.143737+00:00",  //enrich时间
        "code_quality_guarantee" : 0.93744   //模型得分
    }
}
```
# Community-社区服务与支撑模型

index : compass_metric_model_community

```
{
    "_index" : "compass_metric_model_community",
    "_id" : "9d6d71855a55b1629af3db92c463d36947c20109",
    "_score" : null,
    "_source" : {
      "uuid" : "9d6d71855a55b1629af3db92c463d36947c20109",  //uuid
      "level" : "repo",  //级别 repo:单仓  community:多仓
      "type" : null,  //类型  单仓时:null  多仓时(制品仓:software-artifact 治理仓:governance)
      "label" : "https://gitee.com/mindspore/mindspore",   //标签  单仓库时:具体仓库地址  多仓时:具体组织
      "model_name" : "Community Support and Service",  //模型名称
      "issue_first_reponse_avg" : 6.2844, //issue首次响应平均时间 (过去90天新建Issue首次响应均值（天）)
      "issue_first_reponse_mid" : 1.935, //issue首次响应中间时间
      "issue_open_time_avg" : 24.457,  //issue处理平均时间 (过去90天新建Issue的处理时间（天）)
      "issue_open_time_mid" : 15.74,  //issue处理中间时间
      "bug_issue_open_time_avg" : 23.3333,   //bug issue处理平均时间 (过去90天新建Issue的处理时间（天）)
      "bug_issue_open_time_mid" : 14.06,  //issue处理中间时间
      "pr_open_time_avg" : 24.1078,  //pr处理平均时间 (过去90天新建PR的处理时间（天）均值)
      "pr_open_time_mid" : 10.115,  //pr处理中间时间
      "pr_first_response_time_avg" : 2.5293, //pr首次响应平均时间 (过去90天新建PR首次响应均值（天）)
      "pr_first_response_time_mid" : 0.8315, //pr首次响应中间时间
      "comment_frequency" : 1.3526,  //issue评论平均数 (过去90天新建Issue评论数的均值)
      "code_review_count" : 3.2385472554684274, //pr评论平均数 (过去90天新建的PR评论数的均值)
      "updated_issues_count" : 2422, //issue更新数 (过去90天issue更新的个数)
      "closed_prs_count" : 4931, //pr关闭数 (过去90天PR close的个数)
      "grimoire_creation_date" : "2022-11-14T00:00:00+00:00",  //数据统计时间
      "metadata__enriched_on" : "2022-11-19T11:27:01.595195+00:00",  //enrich时间
      "community_support_score" : 0.6333516990238537  //模型得分
    }
}
```
# Organizations Activity-组织活跃度模型

index : compass_metric_model_group_activity

```
{
    "_index" : "compass_metric_model_group_activity",
    "_id" : "24c96c972b414c13146570ca1c57f0a48f7b7b07",
    "_score" : null,
    "_source" : {
        "uuid" : "24c96c972b414c13146570ca1c57f0a48f7b7b07",  //uuid
        "level" : "repo",  //级别 repo:单仓  community:多仓
        "type" : null,  //类型  单仓时:null  多仓时(制品仓:software-artifact 治理仓:governance)
        "label" : "https://gitee.com/mindspore/mindspore",  //标签  单仓库时:具体仓库地址  多仓时:具体组织
        "model_name" : "Organizations Activity",  //模型名称
        "org_name" : "Huawei",  //组织名称
        "is_org" : true,  //是否是组织
        "contributor_count" : 258,  //开发者数量 (过去90天活跃的D2开发者数量（有组织归属的）)
        "contributor_org_count" : 245,  //每个组织的开发者数量 (每个组织过去90天活跃的D2开发者数量)
        "commit_frequency" : 541.9455,  // 提交平均次数 (过去90天每周提交的平均次数（有组织归属的）)
        "commit_frequency_org" : 6917,  //每个组织的提交个数 (每个组织过去90天提交个数)
        "commit_frequency_org_percentage" : 0.9933, //每个组织占组织提交比例 ( 每个组织过去90天提交占组织提交比例)
        "commit_frequency_percentage" : 0.9379,  //每个组织占总体提交比例 ( 每个组织过去90天提交占总体提交比例)
        "org_count" : 9,  // 组织个数 (过去90天活跃的D2开发者所属组织个数)
        "contribution_last" : 92,  //累计贡献 (过去90天所有组织对社区累计贡献时间（周）)
        "grimoire_creation_date" : "2022-11-14T00:00:00+00:00",   //数据统计时间
        "metadata__enriched_on" : "2022-11-21T06:48:25.548675+00:00",  //enrich时间
        "organizations_activity" : 0.84848  //模型得分
    }
}
```

