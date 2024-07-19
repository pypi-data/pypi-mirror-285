# down 
import os
import sys
import subprocess
from huggingface_hub import login, hf_hub_download

login(token='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')

if len(sys.argv)==2:
    hf_hub_download(repo_id="pinsu/ted_tmp", filename="tmp_file", local_dir=os.getcwd(), local_dir_use_symlinks=False, repo_type="dataset")
    name = sys.argv[1].strip('./')
    source = os.path.join(os.getcwd(), "tmp_file")
    destination = os.path.join(os.getcwd(), name)
    command = ['mv', source, destination]
    subprocess.run(command)

    print("download successful~")
else:
    hf_hub_download(repo_id="pinsu/ted_tmp", filename=sys.argv[1], local_dir=sys.argv[2], local_dir_use_symlinks=False, repo_type="dataset")

