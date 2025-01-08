import os

from dotenv import load_dotenv

from pygrdm import grdm

load_dotenv(verbose=True)
load_dotenv()

access_token = os.environ.get("ACCESS_TOKEN")
client = grdm.GRDMClient(access_token)

node_file = client.fetch_node_file("j4wxd", "/RHEED/auto_rotate/label.csv")

client.download_node(node_file)
