import shutil
import os
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        shutil.rmtree(os.path.join(root, '__pycache__'))
        print(f"Deleted: {os.path.join(root, '__pycache__')}")