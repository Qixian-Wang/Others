Gnerally follow: https://open-ephys.github.io/gui-docs/Developer-Guide/Compiling-the-GUI.html

## Step1:
Build new plugin from vscode:

```shell
cd Build
cmake -G "Visual Studio 17 2022" -A x64 ..
```
This will generate a .sln file

## Step2:
Then build the .sln in Visual studio, this will generate a .dll in ```...\build\release```

### Step3:
Move the .dll to plugin

