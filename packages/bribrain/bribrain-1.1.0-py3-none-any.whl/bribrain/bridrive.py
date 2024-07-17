import os

def upload_bridrive(upload_link, path_file):
  script = "PYTHONHTTPSVERIFY=0 python seaf-share.py put {}".format(" ".join([upload_link, path_file]))
  os.system(script)