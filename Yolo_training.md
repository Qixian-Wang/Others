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

# Second: settings and file management
After creating proj, go to **setting -> labeling interface -> code** to set labeling methods.

Example:
```python
<View>
  <Header value="Select a tool and annotate the image"/>
  <Image name="image" value="$image" rotateControl="false" zoom="true"/>

  <!-- Rectangle -->
  <RectangleLabels name="rect" toName="image" strokeWidth="2">
    <Label value="Pipette"             background="#FFA39E"/>
    <Label value="Petri dish"          background="#FFC069"/>
    <Label value="Pipette tip holder"  background="#AD8B00"/>
    <Label value="Tube holder"         background="#D3F261"/>
    <Label value="Suction tip"         background="#389E0D"/>
    <Label value="Beaker"              background="#5CDBD3"/>
    <Label value="MEA"                 background="#096DD9"/>
    <Label value="Large centri-tube"   background="#ADC6FF"/>
    <Label value="Middle centri-tube"  background="#9254DE"/>
    <Label value="Mini centri-tube"    background="#F759AB"/>
    <Label value="rectangle bottle"    background="#D4380D"/>
  </RectangleLabels>

  <!-- Brush -->
  <BrushLabels name="brush" toName="image" brushRadius="10" opacity="0.5">
    <Label value="Pipette"             background="#FFA39E"/>
    <Label value="Petri dish"          background="#FFC069"/>
    <Label value="Pipette tip holder"  background="#AD8B00"/>
    <Label value="Tube holder"         background="#D3F261"/>
    <Label value="Suction tip"         background="#389E0D"/>
    <Label value="Beaker"              background="#5CDBD3"/>
    <Label value="MEA"                 background="#096DD9"/>
    <Label value="Large centri-tube"   background="#ADC6FF"/>
    <Label value="Middle centri-tube"  background="#9254DE"/>
    <Label value="Mini centri-tube"    background="#F759AB"/>
    <Label value="rectangle bottle"    background="#D4380D"/>
  </BrushLabels>

  <!-- Polygon -->
  <PolygonLabels name="poly" toName="image" strokeWidth="1" pointSize="small" opacity="0.9">
    <Label value="Pipette"             background="#FFA39E"/>
    <Label value="Petri dish"          background="#FFC069"/>
    <Label value="Pipette tip holder"  background="#AD8B00"/>
    <Label value="Tube holder"         background="#D3F261"/>
    <Label value="Suction tip"         background="#389E0D"/>
    <Label value="Beaker"              background="#5CDBD3"/>
    <Label value="MEA"                 background="#096DD9"/>
    <Label value="Large centri-tube"   background="#ADC6FF"/>
    <Label value="Middle centri-tube"  background="#9254DE"/>
    <Label value="Mini centri-tube"    background="#F759AB"/>
    <Label value="rectangle bottle"    background="#D4380D"/>
  </PolygonLabels>
</View>
```

Then go to cloud storage to add files:
<img width="767" height="445" alt="image" src="https://github.com/user-attachments/assets/3e99da68-f6af-466d-9302-b6a5c7392339" />
**Don't upload files via inport, which will be tricky to share.**

# Third: Sharing files.
Sharing files is quite difficult here. When doing it, I suggest export **yolo_with_image** and **.json**

In yolo_with_image format, you have all the image labeled. (in case there are deleted figures)
But the file names are modified badly, you can use it to convert the names:

```python
from pathlib import Path
import shutil

# Specify image directory
img_path = Path("Path/to/Image/Folder/in/Your/Export")
# Iterate through all files in the directory (no subdirectories)
for file in img_path.iterdir():
    if file.is_file():
        name = file.name
        new_name = name.split("-", 1)[1]
        new_path = file.with_name(new_name)
        file.rename(new_path)
```

Then since the path of figures are different, you can use it to modify .json file, so the software can recognize it:


```python
import json
import os
import shutil
import re

def replace_paths_in_string(content, d_param):

    def replace_match(match):
        full_path = match.group(0)
        if full_path.lower().endswith('.jpg"'):


            clean_path = full_path[1:-1]
            filename = os.path.basename(clean_path)
            # Remove random string before IMG_
            if 'IMG_' in filename:
                img_part = filename.split('IMG_')[1]
                clean_filename = f"IMG_{img_part}"
            else:
                clean_filename = filename
            new_path = f'"/data/local-files/?d={d_param}{clean_filename}"'
            return new_path
        return full_path
    
    # Match paths surrounded by double quotes
    pattern = r'"\\/data\\/upload\\/1\\/[^"]*\.jpg"'
    return re.sub(pattern, replace_match, content)


def main():
    # Path
    input_path = "Path/to/Image/Folder/in/Your/Export"
    output_path = "output.json"
    file_name = "lab_tool_data%5C"

    if not os.path.isfile(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    # Copy file
    shutil.copy2(input_path, output_path)
    print(f"Input file copied to: {output_path}")

    # Read file
    with open(output_path, "r", encoding="utf-8") as outfile:
        content = outfile.read()

    # Replace paths
    updated_content = replace_paths_in_string(content, file_name)

    # Write file
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(updated_content)

    print(f"Addresses updated in: {output_path}")


if __name__ == "__main__":
    main()
```

This should make it possible to share figures.
