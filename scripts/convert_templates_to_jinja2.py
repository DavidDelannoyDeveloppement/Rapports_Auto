
import os
import re

project_root = os.path.dirname(os.path.dirname(__file__))  # remonte à la racine du projet
templates_dir = os.path.join(project_root, "app", "templates")

def convert_to_jinja2_syntax(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(r"(?<!{){([a-zA-Z0-9_]+)}(?!})", r"{{ \1 }}", content)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith(".html"):
            convert_to_jinja2_syntax(os.path.join(root, file))

print("✅ Conversion terminée.")
