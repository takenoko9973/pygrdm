import os

from dotenv import load_dotenv

from pygrdm import grdm

load_dotenv(verbose=True)
load_dotenv()

access_token = os.environ.get("ACCESS_TOKEN")
client = grdm.GRDMClient(access_token)

print(client.fetch_file_url("j4wxd", "/raw/RHEED"))
