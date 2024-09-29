# Documentation

These are the specific descriptions to the models:

- [开发者基础信息](./developer_model/%E5%BC%80%E5%8F%91%E8%80%85%E6%8A%80%E6%9C%AF%E8%83%BD%E2%BC%92.md)
- [协作倾向模型](./developer_model/%E5%8D%8F%E4%BD%9C%E5%80%BE%E5%90%91%E6%A8%A1%E5%9E%8B.md)
- [成长性模型](./developer_model/%E6%88%90%E2%BB%93%E6%80%A7%E6%A8%A1%E5%9E%8B.md)
- [技术能力模型](./developer_model/%E5%BC%80%E5%8F%91%E8%80%85%E6%8A%80%E6%9C%AF%E8%83%BD%E2%BC%92.md)
- [贡献模型](./developer_model/%E8%B4%A1%E7%8C%AE%E6%A8%A1%E5%9E%8B.md)

## Overview

The main.py file is where the entire program is executed. Each model is written as a separate class, and data is retrieved by calling methods from these classes within main.py. The results are then written to a JSON file.

To check the output data, please refer to the data_request folder, where the JSON files are stored.

## Important Node

There is a unknown calculation error and a bug in the program design for the model "CollaborationTendency". As a result, I did not include a method to call this class in main.py. These issues with the CollaborationTendency model will be addressed and corrected in future updates.