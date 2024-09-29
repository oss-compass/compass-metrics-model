<!--
 * @Descripttion: 
 * @version: V1.0
 * @Author: zyx
 * @Date: 2024-09-16 09:05:18
 * @LastEditors: zyx
 * @LastEditTime: 2024-09-29 08:09:05
-->
# User satisfaction insight model

--------------------------------------------------------------------------------
## Project Overview

--------------------------------------------------------------------------------
The user satisfaction insight model deeply understands the user's satisfaction with open source projects by analyzing key indicators such as user usage frequency, community popularity, and project user attention. This approach not only reveals what users actually need, but also provides a direction for development teams to improve to optimize the user experience. Through continuous user feedback and data analysis, the team was able to adjust the project's features to better align with users' real-world usage scenarios, thereby improving user satisfaction, driving the project's continued development, and enhancing the stability and vitality of the entire open source ecosystem. At present, the model is mainly applied to the three open source central warehouses of pypi, npm and OpenHarmony, and each metric has been described and analyzed in detail to ensure the accuracy of the evaluation.

--------------------------------------------------------------------------------
## Basic information of the indicator
--------------------------------------------------------------------------------
1. **Average handling time for bug issues**: Average handling time (days) for newly created bug issues in the last 90 days, including closed and open issues.
2. **Comprehensive Downloads**: The total number of downloads of software packages in the past 90 days, including the number of downloads of the image source and the package management tool itself.
3. **Popularity**: In the past 90 days, the popularity of the image source and the basic information of star in github/gitee.
4. **Software universality**: The trial status of the software or project in different industries under the latest version, that is, whether the software can be used in multiple industries.
5. **Version Update Stability**: The difference between the time of the last version update and the average update time.


--------------------------------------------------------------------------------
##	Installation Guide
--------------------------------------------------------------------------------
This project requires python>=3.8x, and it is recommended to use a virtual environment to create it
1. Create a virtual environment
```bash
python3.8 -m venv myenv
```
2. Activate the virtual environment
```bash
source myenv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
   
```python
from user_model import USER_MODEL
user = USER_MODEL("https://github.com/pytorch/pytorch")
# a = USER_MODEL("https://ohpm.openharmony.cn/#/cn/detail/@piaojin%2Fpjtabbar")
# a.user_model_score()
# a = USER_MODEL("https://github.com/jquery/jquery")
# a.user_model_score()
```

--------------------------------------------------------------------------------
## Communicate information

--------------------------------------------------------------------------------
New plugins will be added gradually after this project, if you are interested, you can contact me, zyx72038@hust.edu.cn