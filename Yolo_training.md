# First: install labeling tools
The tool used here is label-studio.
For detailed introduction, follow the instruction here: https://github.com/HumanSignal/label-studio

To begin with, install MSVC here: [https://visualstudio.microsoft.com/zh-hans/downloads/](https://visualstudio.microsoft.com/)

Install: **Desktop development with C++**, **MSVC v143 - VS 2022 C++ x64/x86 building tool** and **windows SDK**

Then open **Developer Command Prompt for Visual Studio** locally as admin

Then do
```shell
cl
```

Run following commands here as well.

To install label-studio locally with pip, python version should **below 3.13**:
```python
# Requires Python >=3.8
pip install label-studio

# Start the server at http://localhost:8080
label-studio
```
Then you will find login page, if it is frozen, restart it will do.

# Second: 
