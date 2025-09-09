import subprocess
import re
import sys

if len(sys.argv) != 4:
    print("Usage: python generate_icons.py <icon_list.txt> <output_font_base> <font_size>")
    sys.exit(1)

input_file = sys.argv[1]
output_font_base = sys.argv[2]  # e.g., "icons"
font_size = sys.argv[3]         # e.g., "45"

# Read icon codepoints
with open(input_file, "r") as f:
    content = f.read().replace("\n", "")
    icons = [code.strip().upper() for code in content.split(",") if code.strip()]

unicodes_arg = ",".join([f"U+{code}" for code in icons])

# Generate subset TTF
pyftsubset_cmd = [
    "pyftsubset",
    "MaterialIcons-Regular.ttf",
    f"--unicodes={unicodes_arg}",
    f"--output-file={output_font_base}.ttf"
]
subprocess.run(pyftsubset_cmd, check=True)

# Convert TTF to BDF with specified size
otf2bdf_cmd = [
    "otf2bdf",
    f"{output_font_base}.ttf",
    "-o", f"{output_font_base}.bdf",
    "-p", font_size
]
subprocess.run(otf2bdf_cmd, check=True)

# List icons in BDF
print(f"Icons in {output_font_base}.bdf:")
with open(f"{output_font_base}.bdf", "r") as bdf:
    for line in bdf:
        match = re.match(r"^STARTCHAR\s+(\w+)", line)
        if match:
            print(f"- {match.group(1)}")
