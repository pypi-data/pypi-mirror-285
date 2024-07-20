import os

os.system("python -m build")
os.system("python -m twine upload dist/*")
