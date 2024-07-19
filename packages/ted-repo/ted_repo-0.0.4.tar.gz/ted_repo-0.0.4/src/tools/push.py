# push
import os
import sys
from huggingface_hub import HfApi, login

login(token='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')

path = os.path.join(os.getcwd(), sys.argv[1].strip('./'))

if len(sys.argv)==3:
    save_path = sys.argv[2]
else:
    save_path = "tmp_file"

print(path)

api = HfApi()
api.upload_file(
    path_or_fileobj=path,
    path_in_repo=save_path,
    repo_id="pinsu/ted_tmp",
    repo_type="dataset",
    )

print("push successful~")
