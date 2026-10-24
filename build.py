"""Build the NVDA add-on package from the addon folder.

Usage: python build.py
Creates indianNumberReader-<version>.nvda-addon in this folder.
"""
import os
import re
import zipfile

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, "addon")
with open(os.path.join(src, "manifest.ini"), encoding="utf-8") as f:
	version = re.search(r"^version\s*=\s*(\S+)", f.read(), re.M).group(1)
out = os.path.join(here, "indianNumberReader-%s.nvda-addon" % version)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
	for root, dirs, files in os.walk(src):
		dirs[:] = [d for d in dirs if d != "__pycache__"]
		for name in files:
			if name.endswith(".pyc"):
				continue
			path = os.path.join(root, name)
			z.write(path, os.path.relpath(path, src))
print("Created", out)
