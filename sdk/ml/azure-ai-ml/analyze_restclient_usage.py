import os
import re
import glob

def analyze_restclient_usage():
    restclient_path = "/home/kashifkhan/code/azure-sdk-for-python/sdk/ml/azure-ai-ml/azure/ai/ml/_restclient"
    sdk_path = "/home/kashifkhan/code/azure-sdk-for-python/sdk/ml/azure-ai-ml"
    
    # Get actual folders
    actual_folders = set()
    for item in os.listdir(restclient_path):
        if os.path.isdir(os.path.join(restclient_path, item)) and not item.startswith('.'):
            actual_folders.add(item)
    
    # Find imported folders
    imported_folders = set()
    pattern = r'from azure\.ai\.ml\._restclient\.([^.\s]+)'
    
    for py_file in glob.glob(f"{sdk_path}/**/*.py", recursive=True):
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                matches = re.findall(pattern, content)
                imported_folders.update(matches)
        except:
            continue
    
    print("Actual folders:", sorted(actual_folders))
    print("Imported folders:", sorted(imported_folders))
    print("Unused folders:", sorted(actual_folders - imported_folders))
    print("Missing folders:", sorted(imported_folders - actual_folders))

# Run the analysis
analyze_restclient_usage()