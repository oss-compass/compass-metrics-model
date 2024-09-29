
# Ascend Extension for PyTorch

## Overview

T
1. **Install PyTorch**

Install **PyTorch** through pip.

**For Aarch64:**

```Python
pip3 install torch==2.1.0
```

**For x86:**

```Python
pip3 install torch==2.1.0+cpu  --index-url https://download.pytorch.org/whl/cpu

3. **Install torch-npu**

```
pip3 install torch-npu==2.1.0.post3
```

### From Source

In some special scenarios, users may need to compile **torch-npu** by themselves.Select a branch in table [Ascend Auxiliary Software](#ascend-auxiliary-software) and a Python version in table [PyTorch and Python Version Matching Table](#pytorch-and-python-version-matching-table) first. The docker image is recommended for compiling torch-npu through the following steps(It is recommended to mount the working path only and avoid the system path to reduce security risks.), the generated .whl file path is ./dist/:

1. **Clone torch-npu**


4. **Compile torch-npu**

   Take **Python 3.8** as an example.

   ```
   cd /home/pytorch
   bash ci/build.sh --python=3.8
   ```

## Getting Started

### Prerequisites

Initialize **CANN*
You can quickly experience **Ascend NPU** by the following simple examples.

```Python
import torch
import torch_npu

e phases:
Ascend Extension for PyTorch has a BSD-style license, as found in the [LICENSE](LICENSE) file.
