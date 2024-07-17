#=============================================================#
###  CREATED AT     : 12 MARET 2024                         ###
###  UPDATED AT     : 17 JULI 2024                          ###
###  COPYRIGHT      : BRIBRAIN DATA ENGINEER TEAM           ###
###  DESCRIPTION    : Module untuk kumpulan function        ###
#=============================================================#

from time import time
from pytz import timezone
from datetime import datetime, timedelta
from pyspark.sql import functions as F


#=============================================================#
def try_or(func, default=None, expected_exc=(Exception,)):
  """Menangkap error dan memberikan keluaran sesuai parameter

  Args:
      func (function): python function
        (notes is ditambahkan lambda pada sebelum nama function, ex: try_or(lambda:func))
      default (object): keluaran yang diharapkan ketika terjadi error
      expected_exc (Exception): Exception yang diharapkan
    
  Returns:
      object: keluaran dari function atau mengembalikan keluaran sesuai input jika terdapat error
  """
  
  try:
    return func()
  except expected_exc:
    return default
  
#=============================================================#    
def set_timer():
  """Menetapkan waktu awal untuk penghitungan durasi proses

  Args:
      -
    
  Returns:
      float: waktu dalam format float
  """
    
  global START_TIME
  START_TIME = time()
  
  return START_TIME

#=============================================================#
def get_timer(start_time=None):
  """Memperoleh durasi proses berdasarkan waktu awal dikurangi waktu sekarang

  Args:
      start_time (float) : 
    
  Returns:
      string: durasi proses dengan format HH:MM:SS
  """
    
  if start_time:
    return (datetime(1,1,1)+timedelta(seconds=int(time()-start_time))).strftime("%H:%M:%S")
  
  return (datetime(1,1,1)+timedelta(seconds=int(time()-START_TIME))).strftime("%H:%M:%S")

#=============================================================#  
def get_list_partition(spark, schema, table):
  """Memperoleh list partisi dari hive table yang diurutkan dari partisi terbaru

  Args:
      spark (pyspark.sql.session.SparkSession): spark session
      schema (str): nama schema dari table di hive
      table (str): nama table di hive
    
  Returns:
      list: list partisi diurutkan dari partisi yang terbaru
  """
  
  try:
    partitions = spark.sql("""
     SHOW PARTITIONS {}.{}
     """.format(schema, table)).sort("partition", ascending=False).collect() # ambil partisi sesuai format
    if len(partitions) != 0: # jika ada partisi
      list_partition = []
      for row in partitions:
        if "__HIVE_DEFAULT_PARTITION__" not in row[0]:
          arrange = []
          dict_partition = {}
          for partition in row[0].split("/"):
            value = partition.split("=")
            arrange.append(value[1].zfill(2))
            dict_partition[value[0]] = value[1]
          dict_partition["__formatted_partition"] = "|".join(arrange)
          list_partition.append(dict_partition)
      list_partition = sorted(list_partition, key=lambda row: row['__formatted_partition'], reverse=True)
      return list_partition
    else: # selain itu
      return None # tidak ada partisi
  except:
    print("is not a partitioned table")
    return None
  
#=============================================================#
def get_first_partition(spark, schema, table):
  """Memperoleh partisi pertama dari hive table

  Args:
      spark (pyspark.sql.session.SparkSession): spark session
      schema (str): nama schema dari table di hive
      table (str): nama table di hive
    
  Returns:
      dict: partisi pertama
  """
    
  partitions = get_list_partition(spark, schema, table)
  if partitions == None:
    return None
  
  return partitions[-1]

#=============================================================#  
def get_last_partition(spark, schema, table):
  """Memperoleh partisi terakhir dari hive table

  Args:
      spark (pyspark.sql.session.SparkSession): spark session
      schema (str): nama schema dari table di hive
      table (str): nama table di hive
    
  Returns:
      dict: partisi terakhir
  """
    
  partitions = get_list_partition(spark, schema, table)
  if partitions == None:
    return None
  
  return partitions[0]


#=============================================================#
#=============================================================#

import os

#=============================================================#
def put_to_bridrive(file_path, upload_url):
  """Mengirimkan file dari CDSW ke BRIDrive

  Args:
      upload_url (str): upload link dari Seafile (BRIDrive) untuk upload file
      file_path (str): path file yang akan di upload dari CDSW ke BRIDrive
    
  Returns:
      -
  """

  res = os.system("hdfs dfs -get /user/bribrain_sac/packages/seaf-share.py")

  script = "PYTHONHTTPSVERIFY=0 python seaf-share.py put {}".format(" ".join([upload_url, file_path]))
  os.system(script)
  
  os.remove("/home/cdsw/seaf-share.py")
  
  
#=============================================================# 
def put_to_hdfs(file_path, hdfs_path = "/tmp/development/bribrain"):
  """Mengirimkan file dari CDSW ke HDFS

  Args:
      file_path (str): path file yang akan di upload dari CDSW ke HDFS
      hdfs_path (str): path lokasi penyimpanan data di HDFS
          (default is /tmp/development/bribrain)
    
  Returns:
      -
  """
  command = "hdfs dfs -put {0} {1}".format(file_path, hdfs_path)
  res = os.system(command)
  if res == 0:
    print("success - put: `{0}` to `{1}`".format(file_path, hdfs_path))

    
#=============================================================#
def get_from_hdfs(file_path, cdsw_path = "/home/cdsw/"):
  """Mengambil file dari HDFS ke CDSW

  Args:
      file_path (str): path file yang akan dipindahkan dari HDFS ke CDSW
      cdsw_path (str): path penyimpanan file di HDFS yang ingin dipindahkan
          (default is "/home/cdsw/")
    
  Returns:
      -
  """
  command = "hdfs dfs -get {0} {1}".format(file_path, cdsw_path)
  res = os.system(command)
  if res == 0:
    print("success - get: `{0}` to `{1}`".format(file_path, cdsw_path))


#=============================================================#
def list_file_hdfs(hdfs_path = "/user/{}/".format(os.environ["HADOOP_USER_NAME"])):
  """Memperlihatkan list file yang ada pada lokasi HDFS

  Args:
      hdfs_path (str): path HDFS yang ingin di show
          (default is "/user/{username}/")
    
  Returns:
      -
  """
  command = "hdfs dfs -ls {}".format(hdfs_path)
  res = os.system(command)



