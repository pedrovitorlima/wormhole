import subprocess
import re

# Read icon codepoints from a file (comma-separated or one per line)
with open("icon_list.txt", "r") as f:
    content = f.read().replace("\n", "")
    icons = [code.strip().upper() for code in content.split(",") if code.strip()]

# Format for pyftsubset: U+CODE,U+CODE,...
unicodes_arg = ",".join([f"U+{code}" for code in icons])

# Run pyftsubset to generate icons.ttf
pyftsubset_cmd = [
    "pyftsubset",
    "MaterialIcons-Regular.ttf",
    f"--unicodes={unicodes_arg}",
    "--output-file=icons.ttf"
]
subprocess.run(pyftsubset_cmd, check=True)

# Run otf2bdf to generate icons.bdf at pixel size 45
otf2bdf_cmd = [
    "otf2bdf",
    "icons.ttf",
    "-o", "icons.bdf",
    "-p", "45"
]
subprocess.run(otf2bdf_cmd, check=True)

# List the icons in the final .bdf font file
print("Icons in icons.bdf:")
with open("icons.bdf", "r") as bdf:
    for line in bdf:
        match = re.match(r"^STARTCHAR\s+(\w+)", line)
        if match:
            char_name = match.group(1)
            print(f"- {char_name}")