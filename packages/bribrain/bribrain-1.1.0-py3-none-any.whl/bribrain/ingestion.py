#=============================================================#
###  CREATED AT     : 18 MARET 2024                         ###
###  UPDATED AT     : 23 APRIL 2024                         ###
###  COPYRIGHT      : ANDRI ARIYANTO                        ###
###  DESCRIPTION    : Module untuk melakukan ingest data    ###
#=============================================================#

import os # memungkinkan pengguna untuk berinteraksi dengan sistem operasi yang dijalankan sekarang
import re # membantu mencocokkan atau menemukan string atau set string lainnya, menggunakan sintaksis khusus yang dimiliki suatu pola.
import json # untuk mengubah kamus python menjadi string JSON yang dapat ditulis menjadi file
import subprocess # memungkinkan untuk menelurkan proses baru, terhubung ke pipa input / output / error, dan mendapatkan kode kembali.
from time import time # memasukkan waktu
from pytz import timezone # memasukkan zona waktu
from pyspark.sql import functions as F # memasukkan fungsi dari pyspark
from datetime import datetime, timedelta # Durasi yang mengekspresikan perbedaan antara dua tanggal, waktu, atau instance waktu ke resolusi mikrodetik.
from dateutil.relativedelta import relativedelta # Menerapkan pada datetime yang ada dan dapat menggantikan komponen spesifik dari datetime, atau mewakili interval waktu
from pyspark.sql.types import StructType, StructField, StringType, TimestampType # memasukkan struktur tipe yang berada pada pyspark


# 1 ===================================================================================================================================================================================================
def ingest_to_hive(spark, params):  
  """Orchestrator untuk proses standard ingestion
  
  Parameters:
      df: Spark DataFrame input
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return:
      dict: parameter-parameter hasil yang disimpan dalam bentuk dictionaries
  """  
  t0 = set_ingest_timer()
  dt0 = set_datetime()

  params = get_additional_attributes(params)
  params["formatted_source_schema"] = params["source_schema"]
  params["formatted_source_table"] = params["source_table"]
  params["hive_partition_date"] = params["hive_partition_ingest"]
  try:
    start_time = set_ingest_timer()
    params["job_time"] = "{}:{}:{}".format(str(dt0.hour), str(dt0.minute).zfill(2), str(dt0.second).zfill(2))
    if params["is_periodic"].upper() == "PERIODIC":
      print("INGESTION PERIODIC {}".format(params["strategy"]))
      # check source database exist
      if not is_source_database_exist(spark, params):
        raise Exception("Source database not found")
      # check source table exist
      if not is_source_table_exist(spark, params):
        raise Exception("Source table not found")
      # load data source
      df, params = get_source_table(spark, params)
      # check data source is empty
      params["rows_source"] = get_source_count(df) 
      if params["rows_source"] <= 0:
        raise ValueError("Source table is empty")
      # add partition column to dataframe
      df = add_partition_column(df, params)
      df = set_column_rename(df, params)
      df = set_column_delimiter(df)
      df = update_schema_table(spark, df, params)
      params = get_repartition_number(spark, df, params)
      df, params = ingest_hive_table_periodic(spark, df, params)  
    else:
      print("INGESTION NON PERIODIC {}".format(params["strategy"]))
      # check source database exist
      if not is_source_database_exist(spark, params):
        raise Exception("Source database not found")
      # check source table exist
      if not is_source_table_exist(spark, params):
        raise Exception("Source table not found")
      # load data source
      df, params = get_source_table(spark, params)
      # check data source is empty
      params["rows_source"] = get_source_count(df) 
      if params["rows_source"] <= 0:
        raise ValueError("Source table is empty")
      # add partition column to dataframe
      df = set_column_rename(df, params)
      df = set_column_delimiter(df)
      df = update_schema_table(spark, df, params)
      params = get_repartition_number(spark, df, params)
      df, params = ingest_hive_table_non_periodic(spark, df, params)
    params["rows_hive"] = get_hive_count(spark, params)
    params["ingest_time"] = get_ingest_timer_string(start_time)
    params["status"] = "SUCCESSFUL"
  except ValueError as e:
    print("ERROR (ValueError): ", e)
    params["status"] = "FAILURE"
    params["status_desc"] = "(ValueError): "+str(e).replace("\n","|")
  except Exception as e:
    print("ERROR: ", e)
    params["status"] = "FAILURE"
    params["status_desc"] = ": "+str(e).replace("\n","|")
  finally:
    params = update_additional_attributes(spark, params)
    params["job_period"] = None
    params["running_time"] = get_ingest_timer_string(t0)
    
    return params
# 2 ===================================================================================================================================================================================================
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
# 3 ===================================================================================================================================================================================================
def add_partition_column(df, params):
  """Menambahkan kolom yang akan digunakan sebagai partisi pada Spark DataFrame
  
  Parameters:
      df: Spark DataFrame input
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return:
      spark.DataFrame: Spark DataFrame yang telah memiliki kolom untuk dijadikan sebagai partisi
  """
  hive_partition_col = params["hive_partition_col"].split("|") # proses memecah kolom partisi input menjadi list
  hive_partition_date = params["hive_partition_date"].split("|") # proses memecah value partisi input menjadi list
  hive_partition_format = params["hive_partition_format"].replace('@','').split("|") # proses memecah format partisi input menjadi list
  hive_partition_source = params["hive_partition_source"] # menyimpan source column sebagai acuan partisi dari input ke variabel
  
  i = 0 # mendefinisikan variable pencacah
  # melakukan kondisional terhadap value hive_partition_source
  if hive_partition_source != None and hive_partition_source.strip() != "": # kondisi ketika hive_partition_source memiliki value
    hive_partition_source = hive_partition_source.split("|") # hive_partition_source dipecah menjadi list berdasarkan "|"
    # melakukan perulangan untuk menambahkan kolom partisi sebanyak list input
    while i < len(hive_partition_col): # kondisi perulangan true ketika variable pencacah lebih kecil dari panjang list hive_partition_source
      source_col = hive_partition_source[i].replace('}','').split("{") # proses untuk memperoleh source column
      df = df.withColumn(hive_partition_col[i], F.from_unixtime(F.unix_timestamp(F.col(source_col[0]).cast("string"), source_col[1]), hive_partition_format[i])) # proses penambahan kolom partisi dan isinya yang mengacu pada source column
      i += 1 # menambahkan 1 nilai pencacah
  else: # kondisi ketika hive_partition_source tidak memiliki value
    # melakukan perulangan untuk menambahkan kolom partisi sebanyak list input
    while i < len(hive_partition_col): # kondisi perulangan true ketika variable pencacah lebih kecil dari panjang list hive_partition_col
      df = df.withColumn(hive_partition_col[i], F.lit(hive_partition_date[i])) # proses penambahan kolom dan nilainya yang mengacu pada hive_partition_date
      i += 1# menambahkan 1 nilai pencacah
  return df # return Spark DataFrame yang ditambahkan kolom partisi
# 4 ===================================================================================================================================================================================================
def drop_hive_table(spark, params):  
  """Menghapus tabel pada hive 
  
  Parameters:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  """
  hive_mode = params["strategy"].upper() # menyimpan strategy ingest Capitalize
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive table
  
  # melakukan kondisional sesuai strategy ingest
  if hive_mode == "OVERWRITE": # kondisi ketika strategy ingest overwrite
    query_drop = "DROP TABLE IF EXISTS {}.transit_{}".format(hive_schema, hive_table) # membuat query drop table tabel transit jika ada
  else: # kondisi ketika strategy ingest selain overwrite
    query_drop = "DROP TABLE IF EXISTS {}.{}".format(hive_schema, hive_table) # membuat query tabel target jika ada
  spark.sql(query_drop) # menjalankan query drop table
# 5 ===================================================================================================================================================================================================
def get_additional_attributes(params):
  params["hive_partition_date"] = None
  params["hive_partition_source"] = None
  params["hive_rename_col"] = None
  params["hive_blocksize"] = 0
  params["formatted_source_schema"] = None
  params["formatted_source_table"] = None
  params["formatted_source_query"] = None
  params["sample_schema"] = None
  params["sample_table"] = None
  params["storage_path"] = None
  params["partition_path"] = None
  params["initial_ingest"] = True
  params["partition_ingest"] = None
  params["partition_distinct"] = None
  params["partition_size"] = 0
  params["file_size"] = 0
  params["repartition_number"] = None
  params["repartition_column"] = None
  params["first_partition"] = None
  params["last_partition"] = None
  params["rows_source"] = 0
  params["rows_hive"] = 0
  params["total_rows"] = 0
  params["created_date"] = None
  params["created_by"] = None
  params["user_ingestion"]= None
  params["job_period"] = None
  params["job_time"] = None
  params["running_time"] = None
  params["ingest_time"] = None
  params["dttm_ingest"] = None
  params["last_date_ingest"] = None
  params["activity"] = None
  params["activity_desc"] = None
  params["status"] = None
  params["status_desc"] = None
  params["tool"] = "CDSW"
  params["ds"] = None
  return params
# 6 ===================================================================================================================================================================================================
def get_delta_datetime(dt0, dt1):
  """Mendapatkan selisi tanggal waktu input
  
  Parameters:
      dt0: representasi tanggal waktu sebelumnya dalam tipe datetime.datetime
      dt1: representasi tanggal waktu terkini dalam tipe datetime.datetime
  
  Return:
      datetime.datetime: hasil kalkulasi tanggal waktu
  """
  return dt1-dt0 # return kalkulasi tanggal waktu
# 7 ===================================================================================================================================================================================================
def get_describe_formatted(spark, params, col_name):
  """Mendapatkan informasi dari metadara tabel target 
  
  Parameters:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      col_name: string nama kolom yang akan dicari informasi metadatanya
  
  Return:
      string: informasi metadata yang dicari dari tabel target (None jika tidak ada)
  """
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive table
  
  # penanganan error ketika tabel target tidak tersedia
  try:
    # menjalankan query describe formatted table untuk memperoleh informasi metadata
    return spark.sql(""" 
      DESCRIBE FORMATTED {}.{}
    """.format(hive_schema, hive_table))\
    .select("data_type")\
    .where("UPPER(col_name) = '{}'".format(col_name.upper()))\
    .collect()[0][0] # fungsi collect untuk mendapatkan data dalam bentuk string
  except:
    return None # return None jika tabel target tidak tersedia
# 8 ===================================================================================================================================================================================================
def get_file_size(spark, params, last=False):
  """Mendapatkan folder size secara aktual dari direktori tabel target
  
  Parameters:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      last: boolean untuk menetapkan ukuran keseluruhan data atau hanya partisi terakhir (default False = ukuran data keseluruhan)
  
  Return:
      int: ikuran folder besaran bytes dalam tipe integer
  """
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive table
  last_partition = params["last_partition"] # menyimpan value partisi terakhir dari tabel target (None jika bukan tabel berpartisi)
  
  if hive_schema.startswith("dev"):
    hdfs_path = "/dev/"
  else:
    hdfs_path = "/user/hive/warehouse/"

  # penanganan error ketika direktori tujuan tidak tersedia
  try:
    path = lambda p: spark._jvm.org.apache.hadoop.fs.Path(p) # membuat variabel path untuk menunjukan lokasi direktori pada hive
    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration()) # membuat variabel untuk dapak mengakses File System pada hive
    
    # melakukan kondisional untuk mendapatkan ukuran keseluruhan atau hanya partisi terakhit dari tabel target
    if last and last_partition != None: # kondisi ketika terdapat value pada partisi terakhir dan parameter last True
      hdfs = fs.getContentSummary(path(hdfs_path+"{}.db/{}/{}".format(hive_schema, hive_table, last_partition))) # mendapatkan informasi ukuran hdfs folder partisi terakhir
      return hdfs.getLength() # return ukuran hdfs folder dalam besaran bytes
    else: # kondisi ketika tidak terdapat value pada partisi terakhir atau parameter last False
      hdfs = fs.getContentSummary(path(hdfs_path+"{}.db/{}".format(hive_schema, hive_table))) # mendapatkan informasi ukuran hdfs folder keseluruhan data
      return hdfs.getLength() # return ukuran hdfs folder dalam besaran bytes
  except:
    return 0 # return 0 jika direktori tujuan tidak tersedia
# 9 ===================================================================================================================================================================================================
def get_format_date(format_date):
  """Mengubah format tanggal input menjadi format tanggal sintaks python
  
  Parameter:
      format_date: format tanggal input dalam tipe string
      
  Return:
      string: format tanggal sintaks python
  """
  return format_date.replace("yyyy", "%Y").replace("MM", "%m").replace("dd", "%d") # return string format tanggal hasil pemrosesan
# 10 ==================================================================================================================================================================================================
def get_formatted_attributes(params, step=1):
  """ Mendapatkan format atribut tabel pada hive
  
  Parameter:
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      
  Return:
      format tabel
  """                  
  schema = params["source_schema"] # menyimpan nama source_schema
  table = params["source_table"] # menyimpan nama source_table
  partition = params["partition_ingest"] # menyimpan nama partition_ingest
  partition_format = params["hive_partition_format"] # menyimpan nama hive_partition_format
  check_partition = params["max_partition_to_check"] # menyimpan nama max_partition_to check
  restrict_day = params["restrict_day_to_increment"] # menyimpan nama restrict_day_to_increment
  initial_date = params["initial_date"] # menyimpan nama initial_date
  initial_ingest = params["initial_ingest"] # menyimpan nama initial_ingest
  if partition != None: # checking variable lastPartition
    partition = re.sub(r"\/|[\w_-]+=", "", partition["partition"]) #replaceAll(/\/|[\w_-]+=/,'') # kondisi true->menghilangkan info waktu ex* penghilankan year=,/,month= pada year=2019/month=05 sehingga menjadi 201905
    initial_ingest = False
  else:
    partition = "" # kondisi false
  partition_format = get_format_date(partition_format)
  if partition != "" and not initial_ingest: # checking variable lastPartition dan initialIngest
    partition = datetime.strptime(partition, re.sub(r"\|", "", partition_format)) # kondisi true->menghilangkan info waktu ex* penghilankan tanda | pada yyyy|MM sehingga menjadi yyyyMM
    # variable lastPartition dikonversi menjadi type Date sesuai format
  else:
    partition = datetime.strptime(initial_date, "%Y-%m-%d"); # variable initialDate dikonversi menjadi type Date sesuai format
  now = datetime.now(timezone("Asia/Jakarta")) # mengambil tanggal hari ini
  next_partition = partition # menyalin lastPartition ke nextPartition
  prev = now # menyalin now ke prev
  if not initial_ingest: # checking kondisi initialIngest
    # kondisi true
    if partition_format.lower().find('d') != -1: # checking pertama partitionFormat mengandung day
      prev = now + timedelta(days=check_partition)
      diff_partition = (prev.replace(tzinfo=None) - partition).days
      if diff_partition == step and now.day > restrict_day:
        next_partition = partition + timedelta(days=step)
      elif diff_partition > step:
        next_partition = partition + timedelta(days=step)
    elif partition_format.lower().find('m') != -1: # checking kedua partitionFormat mengandung month
      prev = now + relativedelta(months=check_partition)
      diff_month = prev.month - partition.month
      diff_year = prev.year - partition.year
      diff_partition = diff_month + (diff_year * 12)
      diff_month = now.month - prev.month
      diff_year = now.year - prev.year
      diff_prev = diff_month + (diff_year * 12)
      if diff_partition == step and (now.day > restrict_day or diff_prev > step):
        nextPartition = partition + relativedelta(months=step)
      elif diff_partition > step:
        next_partition = partition + relativedelta(months=step)
    elif partition_format.lower().find('y') != -1: # checking ketiga partitionFormat mengandung year
      prev = now + relativedelta(years=check_partition)
      diff_partition = prev.year - partition.year
      if diff_partition == step and (now.day > restrict_day or now.month > step):
        nextPartition = partition + relativedelta(years=step)
      elif diff_partition >step:
        next_partition = partition + relativedelta(years=step)
  params["hive_partition_date"] = next_partition.strftime(partition_format)
  
  period_format = re.search(r"_*(\{[yYmMdD_\-\*]+\})_*", schema)
  if period_format != None:
    period_format = [period_format.group(), period_format.groups()[0]]
    format_date = get_format_date(re.sub(r"[\{\}\*]", '', period_format[1]))
    if period_format[0].find('*') != -1 and (int(next_partition.strftime(format_date)) >= int(prev.strftime(format_date))):
      if partition_format[0].lower().find('d') != -1 and now.month > next_partition.month:
        value_date = next_partition.strftime(format_date)
        params["formatted_source_schema"] = schema.replace(period_format[1], value_date)                         
      else:                          
        flag = len(period_format[0].replace(period_format[1], ''))
        if flag > 1:
          params["formatted_source_schema"] = schema.replace(period_format[0], '_')
        else:
          params["formatted_source_schema"] = schema.replace(period_format[0], '')
    else:
        value_date = next_partition.strftime(format_date)
        params["formatted_source_schema"] = schema.replace(period_format[1], value_date)
  else:
    params["formatted_source_schema"] = schema
  
  period_format = re.search(r"_*(\{[yYmMdD_\-\*]+\})_*", table)
  if period_format != None:
    period_format = [period_format.group(), period_format.groups()[0]]
    format_date = get_format_date(re.sub(r"[\{\}\*]", '', period_format[1]))
    if period_format[0].find('*') != -1 and (int(next_partition.strftime(format_date)) >= int(prev.strftime(format_date))):
      flag = len(period_format[0].replace(period_format[1], ''))
      if flag > 1:
        params["formatted_source_table"] = table.replace(period_format[0], '_')
      else:
        params["formatted_source_table"] = table.replace(period_format[0], '')
    else:
      value_date = next_partition.strftime(format_date)
      params["formatted_source_table"] = table.replace(period_format[1], value_date)
  else:
    params["formatted_source_table"] = table
    
  return params
# 11 ==================================================================================================================================================================================================
def get_formatted_string(string_input):
  """Mengubah string input menjadi format Capitalize Each Word
  
  Parameter:
      string_input: sebuah kalimat dalam tipe string
      
  Return:
      string: kalimat yang telah terformat
  """
  for i, c in enumerate(string_input): # perulangan setiap huruf yang ada dalam kalimat input
    if i == 0: # ketika huruf merupakan huruf pertama
      output = c.upper() # huruf dijadikan kapital
    elif string_input[i-1] == " ": # ketika sebelumnya space 
      output += c.upper() # huruf dijadikan kapital
    else: # selain itu
      output += c.lower() # huruf dijadikan huruf kecil
  return output # return kalimat yang telah terformat
# 12 ==================================================================================================================================================================================================
def get_hive_count(spark, params):
  """Mendapatkan jumlah hive tabel
  
  Parameter:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return:
      mendapatkan row jumlah data dari hive
  """
  is_periodic = params["is_periodic"].upper() # menyimpan is_periodic dengan huruf kapital
  hive_mode = params["strategy"].upper() # menyimpan strategy dengan huruf kapital
  hive_schema = params["hive_schema"] # menyimpan nama hive_schema
  hive_table = params["hive_table"] # menyimpan nama hive_table
  hive_partition_source = params["hive_partition_source"] # menyimpan nama hive_partition_source
  partition_distinct = params["partition_distinct"] # menyimpan nama partition_distinct
  hive_partition_col = params["hive_partition_col"] # menyimpan nama hive_partition_col
  hive_partition_date = params["hive_partition_date"] # menyimpan nama hive_partition_date
  if is_periodic == "PERIODIC": # cek apabila is_periodic adalah PERIODIC
    hive_partition_col = hive_partition_col.split("|") # update dengan membagi hive_partition_col
    hive_partition_date = hive_partition_date.split("|") # update dengan membagi hive_partition_date
  else: # selain itu
    if hive_partition_col != None: # cek apabila hive_partition_col kosong
      hive_partition_col = hive_partition_col.split("|") # update dengan membagi hive partition_col
    if hive_partition_date != None: # cek apabila hive_partition_date kosong
      hive_partition_date = hive_partition_date.split("|") # update dengan membagi hive_partition_date
  rows_hive = params["rows_hive"] # menyimpan nama rows_hive
  # menghitung jumlah data ingest
  if hive_partition_source != None and hive_mode != "OVERWRITE": # cek apabila terdapat "overwrite"
    hive_partition_source = hive_partition_source.split("|") # update dengan membagi hive_partition_source
    for partition in partition_distinct: # jika terdapat partisi yang terpisah
      count = 'AND '.join(["{}='{}'".format(hive_partition_col[x].lower(), partition[x]) for x in range(len(hive_partition_col))]) # menjumlahkan partisi sesuai format
      query_count = "SELECT COUNT(*) FROM {}.{} WHERE {}".format(hive_schema, hive_table, count) # mengambil tabel di hive
      rows_hive += spark.sql(query_count).first()[0] # menyimpan query_count di row
  elif hive_mode == "OVERWRITE": # cek apabila hive mode terdapat "overwrite"
    query_count = "SELECT COUNT(*) FROM {}.{}".format(hive_schema, hive_table) # mengambil tabel di hive
    rows_hive += spark.sql(query_count).first()[0] # menyimpan query_count di row
  else: # selain itu
    count = 'AND '.join(["{}='{}'".format(hive_partition_col[x].lower(), hive_partition_date[x]) for x in range(len(hive_partition_col))]) # menjumlahkan partisi sesuai format
    query_count = "SELECT COUNT(*) FROM {}.{} WHERE {}".format(hive_schema, hive_table, count) # mengambil tabel di hive
    rows_hive += spark.sql(query_count).first()[0] # menyimpan query_count di row
  return rows_hive
# 13 ==================================================================================================================================================================================================
def get_job_period(params):
  """ Menentukan periode waktu penanggalan setiap job
  
  Parameter:
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      
  Return:
      string: periode waktu penanggalan dalam format string 
  """                  
  dttm_ingest = params["dttm_ingest"] # waktu terkini saat job dijalankan
  last_date_ingest = params["last_date_ingest"] # waktu terakhir saat job dijalankan
  if dttm_ingest != None and last_date_ingest != None: # checking kondisi kedua parameter apabila semua parameter sudah terisi
    period = dttm_ingest - last_date_ingest # mendapatkan selisih hari dari waktu terkini dan waktu terakhir
    if period.days > 27: # ketika jumlah hari (.days) berjumlah lebih dari 27
      return "MONTHLY" # hasil penanggalan yang ditampilkan berupa bulanan (Monthly)
    elif period.days > 5: # ketika jumlah hari (.days) berjumlah lebih dari 5
      return "WEEKLY" # hasil penanggalan yang ditampilkan berupa mingguan (Weekly)
    else: # selain itu
      return "DAILY" # hasil penanggalan yang ditampilkan berupa harian (Daily)
  else:  # checking kondisi kedua parameter apabila salah satu parameter terisi
    return "DAILY" # hasil penanggalan yang ditampilkan berupa harian (Daily)
# 14 ==================================================================================================================================================================================================
def get_last_date_ingest(spark, params):
  """Mendapatkan waktu terakhir data ingest
  
  Parameter:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return:
      waktu terakhir data ingest
  """
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive tabel
  # mengambil waktu terakhir data pada row 1 pada tabel temporary log activity raw ingestion info
  try:
    return spark.sql("""
      WITH CTE AS (
        SELECT # mengumpulkan semua objek data dalam 1 tabel
          dttm_ingest,
          ROW_NUMBER() OVER (
            PARTITION BY
              hive_schema,
              hive_table
            ORDER BY # mengatur data secara descending
              dttm_ingest DESC
          ) AS row_number
        FROM
          temp.log_activity_raw_dly_ingestion_info # data dari tabel
        WHERE
          hive_schema = '{}'
          AND
          hive_table = '{}'
      ) SELECT * FROM CTE WHERE row_number = 1
    """.format(hive_schema, hive_table)).collect()[0][0] # mengambil waktu terakhir
  except:
    return set_datetime() # atur waktu
# 15 ==================================================================================================================================================================================================
def get_partition(spark, params, first=False):
  """Mendapatkan partisi pada hive
  
  Parameters:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      first: boolean untuk mendapatkan partisi (default False = mengambil data secara descending)
  
  Return:
     Mendapatkan partisi pada hive secara ascending/descending
  """
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive tabel
  # mendapatkan jumlah 2 partisi pada hive secara ascending apabila true dan descending apabila false dengan format yang disesuaikan
  try:
    partition = spark.sql("""
     SHOW PARTITIONS {}.{}
     """.format(hive_schema, hive_table)).sort('partition', ascending=first).limit(2).toJSON().collect() # ambil partisi sesuai format
    if len(partition) != 0: # jika tidak ada partisi
      return json.loads(partition[0] if partition[0].find("__HIVE_DEFAULT_PARTITION__")==-1 else partition[1]) # mencari ke default partisi hive
    else: # selain itu
      return None # tidak ada partisi
  except:
    return None
# 16 ==================================================================================================================================================================================================
def get_repartition_number(spark, df, params):
  """
  Mendapatkan partisi number pada hive
    Condition :
      spark : Objek SparkSession
      df  : Spark DataFrame yang akan dicari jumlah row-nya
      params : parameter-parameter pendukung yang disimpan dalam bentuk dictionaries

  Return : Hasil partisi number

  """
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive tabel
  params["hive_blocksize"] = int(params["repartition_size"])*1024*1024 # update hive_blocksize dengan integer partisi size
  params["sample_schema"] = params["hive_schema"] # update sample schema dengan temporary
  params["sample_table"] = "sample_" + hive_table # update sampel tabel dengan hive tabel
  
  if hive_schema.startswith("dev"):
    hdfs_path = "/dev/"
  else:
    hdfs_path = "/user/hive/warehouse/"
    
  # membuat sampel tabel
  df\
    .sample(False,0.1,None)\
    .write\
    .format("parquet")\
    .mode("overwrite")\
    .saveAsTable("{}.{}".format(params["sample_schema"], params["sample_table"]))
  # mengambil partisi number pada hive temporary
  path = lambda p: spark._jvm.org.apache.hadoop.fs.Path(p)
  fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
  hdfs_folder = fs.getContentSummary(path(hdfs_path+"{}.db/{}/".format(params["sample_schema"], params["sample_table"])))
  # menimpa num_file_partitions ke partisi number aktual
  repartition_number = float(hdfs_folder.getLength()*10)/float(params["hive_blocksize"]) # menambahkan jumlah partisi dengan format float
  params["repartition_number"] = int(1 if repartition_number < 1 else repartition_number)
  # menghapus sampel tabel
  spark.sql("DROP TABLE {}.{}".format(params["sample_schema"], params["sample_table"]))
  return params
# 17 ==================================================================================================================================================================================================
def get_source_count(df):
  """Mendapatkan jumlah row data sumber/Spark DataFrame
  
  Parameter:
      df: Spark DataFrame yang akan dicari jumlah row-nya
  
  Return:
      int: jumlah row DataFrame input
  """
  return df.count() # return jumlah row dari fungsi count Spark DatFrame
# 18 ==================================================================================================================================================================================================
# edit disini untuk menambankan database baru (sudah ditambah postgress dan db2)
def get_source_table(spark, params):
  """Mendapatkan data dari tabel sumber dan melakukan update pada params
  
  Parameters:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      
  Return:
      df: Spark DataFrame yang telah ter-update
      dictionaries: hasil proses update value dari parameter input params
  """
  is_periodic = params["is_periodic"] # menyimpan tipe job yang digunakan
  database_type = params["database_type"] # menyimpan informasi database yang digunakan
  host_ip = params["host_ip"] # menyimpan host ip
  host_port = params["host_port"] # menyimpan host port
  username = params["username"] # menyimpan username
  password = params["password"] # menyimpan password
  hive_partition_date = params["hive_partition_date"] # menyimpan value partisi yang akan di-ingest
  
  # melakukan kondisional terhadap tipe job yang digunakan
  if is_periodic.upper() == "PERIODIC": # kondisi ketika tipe job adalah periodic
    source_database = params["formatted_source_schema"] if params["source_database"] == None else params["source_database"] # menyimpan informasi source_database apabila bukan "PERIODIC" 
    source_schema = params["formatted_source_schema"] # menyimpan source schema yang telah disesuaikan formatnya
    source_table = params["formatted_source_table"] # menyimpan source table yang telah disesuaikan formatnya
    hive_partition_date = hive_partition_date.replace("|", "") # menghilangkan '|' pada value partisi yang akan di-ingest
  else: # kondisi ketika tipe job adalah non periodic
    source_database = params["source_schema"] if params["source_database"] == None else params["source_database"] # menyimpan informasi source_database apabila bukan "PERIODIC" 
    source_schema = params["source_schema"] # menyimpan source schema
    source_table = params["source_table"] # menyimpan source table
    hive_partition_date = "" # mendefinisikan value partisi sebagai string kosong
  source_query = params["source_query"] # menyimpan source query
  
  # pencegahaan error ketika load data pada tabel sumber
  try:
    # melakukan kondisional terhadap tipe database yang digunakan
    if database_type.upper() == "SQL SERVER": # kondisi ketika tipe database adalah sql server
      # melakukan kondisional terhadap source query
      if source_query != None and source_query.strip() != "": # kondisi ketika source query memilki value
        query = source_query.replace("{SCHEMA}", source_schema).replace("|", ",") # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{TABLE}","[" + source_table + "]") # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{NEXT_PARTITION}", hive_partition_date) # mengubah {NEXT_PARTITION} menjadi value partisi ingest
        query = "(" + query + ") AS tmp" # membentuk query select
      else: # kondisi ketika source query tidak memilki value
        query = "(SELECT * FROM [" + source_table + "]) AS tmp" # membentuk query select
      params["formatted_source_query"] = query # update value dengan query yang digunakan untuk perolehan data tabel sumber
      # konfigurasi perolehan data sql server
      df = spark.read.format("jdbc")\
      .option("driver","com.microsoft.sqlserver.jdbc.SQLServerDriver")\
      .option("url","jdbc:sqlserver://{}:{};databaseName={};user={};password={};"\
        .format(host_ip, host_port, source_schema, username, password))\
      .option("dbtable", query)\
      .load()
    elif database_type.upper() == "MYSQL": # kondisi ketika tipe database adalah mysql
      # melakukan kondisional terhadap source query
      if source_query != None and source_query.strip() != "": # kondisi ketika source query memilki value
        query = source_query.replace("{SCHEMA}", source_schema).replace("|", ",") # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{TABLE}", source_table) # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{NEXT_PARTITION}", hive_partition_date) # mengubah {NEXT_PARTITION} menjadi value partisi ingest
        query = "(" + query + ") AS tmp" # membentuk query select
      else: # kondisi ketika source query tidak memilki value
        query = "(SELECT * FROM " + source_table + ") AS tmp" # membentuk query select
      params["formatted_source_query"] = query # update value dengan query yang digunakan untuk perolehan data tabel sumber
      # konfigurasi perolehan data mysql
      df = spark.read.format("jdbc")\
      .option("driver","com.mysql.jdbc.Driver")\
      .option("url","jdbc:mysql://{}:{}/{}".format(host_ip, host_port, source_schema))\
      .option("user", username)\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable", query)\
      .load()
    elif database_type.upper() == "POSTGRES": # kondisi ketika tipe database adalah postgres
      # melakukan kondisional terhadap source query
      if source_query != None and source_query.strip() != "": # kondisi ketika source query memilki value
        query = source_query.replace("{SCHEMA}", source_schema).replace("|", ",") # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{TABLE}", '"{}"'.format(source_table)) # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{NEXT_PARTITION}", hive_partition_date) # mengubah {NEXT_PARTITION} menjadi value partisi ingest
        query = "(" + query + ") AS tmp" # membentuk query select
      else: # kondisi ketika source query tidak memilki value
        query ='(SELECT * FROM {}."{}") AS tmp'.format(source_schema, source_table) # membentuk query select
      params["formatted_source_query"] = query # update value dengan query yang digunakan untuk perolehan data tabel sumber
      # konfigurasi perolehan data mysql
      df = spark.read.format("jdbc")\
      .option("driver","org.postgresql.Driver")\
      .option("url","jdbc:postgresql://{}:{}/{}".format(host_ip, host_port, source_database))\
      .option("user", username )\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable", query)\
      .load()
    elif database_type.upper() == "DB2": # kondisi ketika tipe database adalah db2
      # melakukan kondisional terhadap source query
      if source_query != None and source_query.strip() != "": # kondisi ketika source query memilki value
        query = source_query.replace("{SCHEMA}", source_schema).replace("|", ",") # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{TABLE}", source_table) # mengubah {TABLE} menjadi tabel sumber
        query = query.replace("{NEXT_PARTITION}", hive_partition_date) # mengubah {NEXT_PARTITION} menjadi value partisi ingest
        query = "(" + query + ") AS tmp" # membentuk query select
      else: # kondisi ketika source query tidak memilki value
        query = "(SELECT * FROM {}.{}) AS tmp".format(source_schema, source_table) # membentuk query select
      params["formatted_source_query"] = query # update value dengan query yang digunakan untuk perolehan data tabel sumber
      # konfigurasi perolehan data mysql
      df = spark.read.format("jdbc")\
      .option("driver","com.ibm.db2.jcc.DB2Driver")\
      .option("url","jdbc:db2://{}:{}/{}".format(host_ip, host_port, source_database))\
      .option("user", username )\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable", query)\
      .load()
    
    # melakukan perulangan untuk update tipe data
    for dt in df.dtypes: # perulangan sebanyak kolom dari tabel target
      # melakukan kondisional untuk memeriksa perbedaan tipe data
      if dt[1] == "date": # kondisi ketika tipe kolom dari tabel ingest dan tabel target berbeda
        df = df.withColumn(dt[0], F.col(dt[0]).cast("timestamp")) # update tipe data kolom pada tabel ingest
    return df, params # return Spark DataFrame data tabel sumber dan params yang telah ter-update
  except:
    raise Exception("Cannot get data from source table") # melemparkan error ketika tidak dapat load data tabel sumber
# 19 ==================================================================================================================================================================================================
def get_ingest_timer(prev_timer):
  """Mendapatkan selisi waktu terkini dengan waktu sebelumnya
  
  Parameter:
      prev_timer: representasi waktu sebelumnya dengan tipe float
  
  Return:
      datetime.datetime: representasi waktu selisih
  """
  return datetime(1,1,1)+timedelta(seconds=int(time()-prev_timer)) # return datetime.datetime selisih dari waktu terkini dan waktu input
# 20 ==================================================================================================================================================================================================
def get_ingest_timer_string(prev_timer):
  """Mendapatkan selisi waktu terkini dengan waktu sebelumnya dalam format string
  
  Parameter:
      prev_timer: representasi waktu sebelumnya dengan tipe float
  
  Return:
      string: representasi waktu selisih dalam format string
  """
  t = get_ingest_timer(prev_timer) # mendapatkan datetime.datetime selisih dari waktu terkini dan waktu input
  return "{}:{}:{}".format(str(t.hour).zfill(2),str(t.minute).zfill(2),str(t.second).zfill(2)) # return selisih waktu dengan format string
# 21 ==================================================================================================================================================================================================
def get_total_count(spark, params):
  """Mendapatkan jumlah row data target keseluruhan
  
  Parameter:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return:
      int: jumlah row DataFrame input
  """
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive tabel
  try:
    return spark.sql("SELECT * FROM {}.{}".format(hive_schema, hive_table)).count() # mendapatkan jumlah row data keseluruhan
  except:
    return 0
# 22 ==================================================================================================================================================================================================
def get_username():
  """Mendapatkan username CDSW
  
  Return:
      string: username CDSW
  """
  return os.environ["HADOOP_USER_NAME"] # return hadoop username
# 23 ==================================================================================================================================================================================================
def ingest_hive_table_non_periodic(spark, df, params):
  """
  Meng- ingest tabel non periodik di spark

    Condition :
      spark	: Objek SparkSession
      df		: Spark DataFrame yang akan dicari jumlah row-nya
      params	: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries

  Return	: Hasil tabel non_periodik di spark dataframe

  """
  hive_mode = params["strategy"].lower() # menyimpan nama strategy pada hive_mode
  hive_schema = params["hive_schema"] # menyimpan nama hive_schema pada hive_schema
  hive_table = params["hive_table"] # menyimpan nama hive_table pada hive_table
  repartition_column = params["repartition_column"] # menyimpan nama repartition_colum pada repartition_column
  repartition_number = params["repartition_number"] # menyimpan nama repartition_number pada repartition_number

  if hive_schema.startswith("dev"):
    hdfs_path = "/dev/"
  else:
    hdfs_path = "/user/hive/warehouse/"
    
  if repartition_column != None and repartition_column.strip() != "": # cek repartition_column apabila kosong
    df = df.repartition(repartition_number, repartition_column) # update kolom dengan angka dan kolom
  else: # selain itu
    df = df.repartition(repartition_number) # update kolom dengan nomor partisi

  # load to hive
  if hive_mode.upper() == "APPEND": # cek hive mode dengan kondisi APPEND
    partition =  set_datetime().date().strftime("%Y%m%d") # menyimpan format waktu dan tanggal pada partition
    params["hive_partition_col"] = "ds" # update hive_partition_col dengan dttm_ingest
    params["hive_partition_date"] = str(partition) # update hive_partition_date dengan format string
    df = df.withColumn("ds", F.lit(partition)) # update kolom dengan dttm_ingest
    hive_table_exist = spark.sql("SHOW TABLES IN {} LIKE '{}'".format(hive_schema, hive_table)).count()
    if hive_table_exist == 1:
      query_drop_partition = "ALTER TABLE {}.{} DROP IF EXISTS PARTITION(ds='{}')".format(hive_schema, hive_table, str(partition)) # update query_drop_partition dengan kondisi menghapus tabel dttm ingest dengan format hive_schema, hive_table, str(partition)
      spark.sql(query_drop_partition) # menghapus partisi di spark
    df.write.partitionBy("ds").format("parquet").mode(hive_mode).saveAsTable("{}.{}".format(hive_schema, hive_table)) # membuat tabel dengan partisi berdasarkan dttm ingest pada /user/hive/warehouse/{}.db/{}/ dengan format hive_schema, hive_table
    spark.sql("MSCK REPAIR TABLE {}.{}".format(hive_schema, hive_table)) # memperbaiki tabel
  else: # selain itu
    drop_hive_table(spark, params) # menghapus tabel di spark
    df = df.withColumn("hdfs_dttm_ingest", F.lit(set_datetime())) # membuat kolom tabel berisi dttm_ingest dengan status waktu data ketika di ingest
    df.write.format("parquet").mode(hive_mode).saveAsTable("{}.transit_{}".format(hive_schema, hive_table)) # membuat tabel dengan partisi berdasarkan dttm ingest pada /user/hive/warehouse/{}.db/{}/ dengan format hive_schema, hive_table
    spark.sql("REFRESH TABLE {}.transit_{}".format(hive_schema, hive_table)) # refresh tabel di spark
    spark.sql("DROP TABLE IF EXISTS {}.{}".format(hive_schema, hive_table)) # menghapus tabel jika ada sebelumnya
    spark.sql("ALTER TABLE {0}.transit_{1} RENAME TO {0}.{1}".format(hive_schema, hive_table)) # menyimpan tabel baru
    spark.sql("ALTER TABLE {0}.{1} SET SERDEPROPERTIES('path'='hdfs://bribigdata{2}{0}.db/{1}')".format(hive_schema, hive_table, hdfs_path)) # menyimpan tabel di hive database
  # refresh metadata after modifying sql statement before
  query=""" 
    hive -e 'ALTER TABLE {}.{} SET TBLPROPERTIES("EXTERNAL"="FALSE");' 
  """.format(hive_schema, hive_table) # membuat query untuk dikirimkan ke terminal
  popen = subprocess.Popen(query,shell=True,stderr=subprocess.PIPE) # mengirimkan ke terminal
  stdout,stderr = popen.communicate() # mengirimkan kembali ke hive 
  if popen.returncode != 0: # cek apabila data yang kembali dari terminal berisi kosong
    print(stderr) # mengirimkan standar error
  spark.sql("REFRESH TABLE {}.{}".format(hive_schema, hive_table)) # refresh tabel di spark
  return df, params # # return Spark DataFrame data sumber dan params yang telah ter-update
# 24 ==================================================================================================================================================================================================
def ingest_hive_table_periodic(spark, df, params):
  """
  Meng- ingest tabel periodik di spark

    Condition :
      spark	: Objek SparkSession
      df		: Spark DataFrame yang akan dicari jumlah row-nya
      params	: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries

  Return	: Hasil tabel periodik di spark dataframe

  """
  hive_mode = params["strategy"].lower() # menyimpan nama strategy pada hive_mode
  hive_schema = params["hive_schema"] # menyimpan nama hive_schema pada hive_schema
  hive_table = params["hive_table"] # menyimpan nama hive_table pada hive_table
  hive_partition_col = params["hive_partition_col"].split("|") # menyimpan partisi kolom di hive_partition_col
  hive_partition_source = params["hive_partition_source"] # menyimpan sumber partisi di hive_partition_source
  hive_partition_date = params["hive_partition_date"].split("|") # menyimpan tanggal partisi di hive_partition_date
  repartition_column = params["repartition_column"] # menyimpan kolom partisi di repartition_column
  repartition_number = params["repartition_number"] # menyimpan kolom nomor di repartition_number

  if hive_schema.startswith("dev"):
    hdfs_path = "/dev/"
  else:
    hdfs_path = "/user/hive/warehouse/"

  if repartition_column != None and repartition_column.strip() != "": # cek repartition_column apabila kosong
    df = df.repartition(repartition_number, repartition_column) # update kolom dengan angka dan kolom
  else: # selain itu
    df = df.repartition(repartition_number) # update kolom dengan nomor partisi

  # load to hive
  if hive_mode.upper() == "OVERWRITE": # cek hive apabila kondisi overwrite
    # start
    drop_hive_table(spark, params) # menghapus tabel di spark
    df.write.partitionBy(hive_partition_col).format("parquet").mode(hive_mode).saveAsTable("{}.transit_{}".format(hive_schema, hive_table)) # membuat transit tabel dengan partisi berdasarkan hive_partition_col untuk hive_schema, hive_table
    spark.sql("MSCK REPAIR TABLE {}.transit_{}".format(hive_schema, hive_table)) # memperbaiki tabel berpartisi
    spark.sql("REFRESH TABLE {}.transit_{}".format(hive_schema, hive_table)) # refresh transit tabel di spark
    spark.sql("DROP TABLE IF EXISTS {}.{}".format(hive_schema, hive_table)) # menghapus tabel jika ada sebelumnya
    spark.sql("ALTER TABLE {0}.transit_{1} RENAME TO {0}.{1}".format(hive_schema, hive_table)) # mengubah nama transit tabel
    spark.sql("ALTER TABLE {0}.{1} SET SERDEPROPERTIES('path'='hdfs://bribigdata{2}{0}.db/{1}')".format(hive_schema, hive_table, hdfs_path)) # menyimpan tabel di hive database
  else: # selain itu
    # masih belum menemukan kasus hive_partition_source tidak kosong
    hive_table_exist = spark.sql("SHOW TABLES IN {} LIKE '{}'".format(hive_schema, hive_table)).count()
    if hive_table_exist == 1:
      if hive_partition_source != None: # cek apabila partisi source tidak kosong 
        hive_partition_source = hive_partition_source.spilt("|") # menyimpan sumber partisi di hive_partition_source
        df.write.partitionBy(hive_partition_col).parquet("/user/cdh-etl1/parquet/", mode = 'overwrite') # membuat ulang tabel partisi hive
        df = spark.read.parquet("/user/cdh-etl1/parquet/") # memanggil tabel yang sudah dibuat
        df.createOrReplaceTempView("temp_{}".format(hive_table)) # membuat file temporary dari tabel yang sudah dibuat
        query_distinct = "SELECT DISTINCT {} FROM temp_{}".format(", ".join(hive_partition_col), hive_table) # menambahkan hive_partition_col di query distinct
        partition_distinct = spark.sql(query_distinct).collect() # menambahkan query distinct di partition_distinct
        drop_partition = ', '.join(["{}='{}'".format(hive_partition_col[x].lower(), partition_distinct[x][1]) for x in range(len(hive_partition_col))])
        query_drop_partition = "ALTER TABLE {}.{} DROP IF EXISTS PARTITION({})".format(hive_schema, hive_table, drop_partition) # membuat command untuk menghapus partisi apabila partisi tersebut sudah ada
        spark.sql(query_drop_partition) # menghapus partisi yang sudah tersedia
        params["partition_distinct"] = partition_distinct # update value dengan query yang digunakan untuk perolehan data tabel sumber
      else: # selain itu
        drop_partition = ', '.join(["{}='{}'".format(hive_partition_col[x].lower(), hive_partition_date[x]) for x in range(len(hive_partition_col))]) # membuat command untuk tabel dengan format yang tersedia
        query_drop_partition = "ALTER TABLE {}.{} DROP IF EXISTS PARTITION({})".format(hive_schema, hive_table, drop_partition) # membuat command untuk menghapus tabel apabila data sudah ada
        spark.sql(query_drop_partition) # menghapus tabel pada spark
    df.write.partitionBy(hive_partition_col).format("parquet").mode(hive_mode).saveAsTable("{}.{}".format(hive_schema, hive_table)) # insert tabel partisi ke hive
  query=""" 
    hive -e 'ALTER TABLE {}.{} SET TBLPROPERTIES("EXTERNAL"="FALSE");' 
  """.format(hive_schema, hive_table) # membuat query untuk dikirimkan ke terminal
  popen = subprocess.Popen(query,shell=True,stderr=subprocess.PIPE) # mengirimkan ke terminal
  stdout,stderr = popen.communicate() # mengirimkan kembali ke hive 
  if popen.returncode != 0: # cek apabila data yang kembali dari terminal berisi kosong
    print(stderr) # mengirimkan standar error
  # refresh metadata setelah merubah sql statement sebelumnya
  spark.sql("MSCK REPAIR TABLE {}.{}".format(hive_schema, hive_table)) # memperbaiki tabel di spark
  spark.sql("REFRESH TABLE {}.{}".format(hive_schema, hive_table)) # refresh tabel di spark
  return df, params # return Spark DataFrame data sumber dan params yang telah ter-update
# 25 ==================================================================================================================================================================================================
def ingest_log_activity(spark, params): 
  """ Mencatat setiap aktivitas data yang sudah di ingest
  
  Parameter :
    Spark   : objek SparkSession
    params  : parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return :
    Mendistribusikan data yang sudah dikumpulkan ke dalam tabel
  """
  schema = StructType([ # membuat tabel yang terdiri dari beberapa kolom
    StructField('hive_schema', StringType(), True), # membuat kolom string dengan nama hive_schema yang dapat diisi dengan None
    StructField('hive_table', StringType(), True), # membuat kolom string berisi data tabel hive yang dapat diisi dengan None
    StructField('hive_path', StringType(), True), # membuat kolom string berisi data path hive yang dapat diisi dengan None
    StructField('block_size', StringType(), True), # membuat kolom string berisi data block_size yang dapat diisi dengan None
    StructField('partition_size', StringType(), True), # membuat kolom string berisi data size partisi yang dapat diisi dengan None
    StructField('partition_ingest', StringType(), True), # membuat kolom string berisi partisi ingest yang dapat diisi dengan None
    StructField('total_source_rows', StringType(), True), # membuat kolom string dengan nama total_source rows yang dapat diisi data dengan None
    StructField('total_hive_rows', StringType(), True), # membuat kolom string dengan nama hive_rows yang dapat diisi data dengan None
    StructField('user_ingestion', StringType(), True), # membuat kolom string dengan nama user_ingestion yang dapat diisi data dengan None
    StructField('is_periodic', StringType(), True), # membuat kolom string dengan nama is_periodic yang dapat diisi data dengan None
    StructField('job_period', StringType(), True), # membuat kolom string berisi periode waktu yang dapat diisi data dengan None
    StructField('job_time', StringType(), True), # membuat kolom string berisi waktu setiap data yang dapat diisi data dengan None
    StructField('running_time', StringType(), True), # membuat kolom string berisi catatan waktu yang dapat diisi data dengan None
    StructField('ingest_time', StringType(), True), # membuat kolom string berisi waktu data di ingest dan dapat diisi data dengan None
    StructField('dttm_ingest', TimestampType(), True), # membuat kolom string berisi catatan waktu terkini data di ingest yang dapat diisi data dengan None
    StructField('last_date_ingest', TimestampType(), True), # membuat kolom string berisi catatan waktu data terakhir di ingest yang dapat diisi data dengan None
    StructField('activity', StringType(), True), # membuat kolom string berisi aktivitas data dan kolom dapat diisi data dengan None
    StructField('activity_desc', StringType(), True), # membuat kolom string dengan nama activity_desc yang dapat diisi data dengan None
    StructField('status', StringType(), True), # membuat kolom string berisi status data yang dapat diisi data dengan None
    StructField('status_desc', StringType(), True), # membuat kolom string dengan nama status_desc yang dapat diisi data dengan None
    StructField('tool', StringType(), True), # membuat kolom string dengan nama tools yang dapat diisi data dengan None
    StructField('ds', StringType(), True) # membuat kolom string berisi date string yang dapat diisi data dengan None
  ])
  data = [(
    params["hive_schema"], params["hive_table"], params["partition_path"],
    params["hive_blocksize"], params["partition_size"], params["partition_ingest"],
    params["rows_source"], params["rows_hive"], params["user_ingestion"], 
    params["is_periodic"], params["job_period"], params["job_time"], 
    params["running_time"], params["ingest_time"], params["dttm_ingest"], 
    params["last_date_ingest"], params["activity"], params["activity_desc"],
    params["status"], params["status_desc"], params["tool"], params["ds"] # data yang akan diisi ke tabel
  )]
   # membuat dataframe pada temporary tabel informasi metadata menggunakan format yang sudah tersedia
  spark.createDataFrame(tuple(data), schema)\
    .coalesce(1)\
    .write\
    .partitionBy("ds")\
    .mode("append")\
    .format("parquet")\
    .saveAsTable("dev_ddb.log_activity_raw_ingestion_table") # simpan sebagai tabel log activity
# 26 ==================================================================================================================================================================================================
def ingest_metadata_info(spark, params): 
  """ Mencatat setiap info metadata yang sudah di ingest
	
	Parameter :
		Spark 	: objek SparkSession
		params	: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
	
	Return :
		Mendistribusikan data temp. metadata yang sudah dikumpulkan ke dalam tabel
	"""
  schema = StructType([ # membuat tabel dari beberapa kolom
    StructField('source_type', StringType(), True), # membuat kolom string dengan nama Source type yang dapat diisi dengan None
    StructField('ip', StringType(), True), # membuat kolom string dengan nama ip yang dapat diisi dengan None
    StructField('port', StringType(), True), # membuat kolom string dengan nama port yang dapat diisi dengan None
    StructField('source_database', StringType(), True), # membuat kolom string dengan nama Source_schema yang dapat diisi dengan None
    StructField('source_schema', StringType(), True), # membuat kolom string dengan nama Source_schema yang dapat diisi dengan None
    StructField('source_table', StringType(), True), # membuat kolom string dengan nama Source_table yang dapat diisi dengan None
    StructField('hive_schema', StringType(), True), # membuat kolom string dengan nama hive_schema yang dapat diisi dengan None
    StructField('hive_table', StringType(), True), # membuat kolom string dengan nama hive_table yang dapat diisi dengan None
    StructField('storage_path', StringType(), True), # membuat kolom string dengan nama storage_path yang dapat diisi dengan None
    StructField('file_size', StringType(), True), # membuat kolom string dengan nama file_size yang dapat diisi dengan None
    StructField('total_rows', StringType(), True), # membuat kolom string dengan nama total_rows yang dapat diisi dengan None
    StructField('first_partition', StringType(), True), # membuat kolom string dengan nama first_partition yang dapat diisi dengan None
    StructField('last_partition', StringType(), True), # membuat kolom string dengan nama last_partition yang dapat diisi dengan None
    StructField('created_date', StringType(), True), # membuat kolom string dengan nama created_date yang dapat diisi dengan None
    StructField('created_by', StringType(), True), # membuat kolom string dengan nama created_by yang dapat diisi dengan None
    StructField('dttm_ingest', TimestampType(), True), # membuat kolom string dengan nama dttm_ingest yang dapat diisi dengan None
    StructField('ds', StringType(), True) # membuat kolom string dengan nama ds yang dapat diisi dengan None
  ])
  data = [(
    params["database_type"], params["host_ip"], params["host_port"], params["source_database"],
    params["source_schema"], params["source_table"], params["hive_schema"],
    params["hive_table"], params["storage_path"], params["file_size"],
    params["total_rows"], params["first_partition"], params["last_partition"],
    params["created_date"], params["created_by"], params["dttm_ingest"], params["ds"] # data yang akan diisi ke tabel
  )]
  spark.createDataFrame(tuple(data), schema)\
    .coalesce(1)\
    .write\
    .partitionBy("ds")\
    .mode("append")\
    .format("parquet")\
    .saveAsTable("dev_ddb.metadata_raw_describe_table") # membuat dataframe pada temporary tabel informasi metadata menggunakan format yang sudah tersedia
# 27 ==================================================================================================================================================================================================
# edit disini untuk menambankan database baru (sudah ditambah postgress dan db2)
def is_source_database_exist(spark, params):
  """ Cek database tersedia
 
 Parameter :
  Spark  : objek SparkSession
  params : parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
 
 Return :
  Menampilkan database yang tersedia
 """
  database_type = params["database_type"] # menyimpan informasi database yang digunakan
  host_ip = params["host_ip"] # menyimpan informasi ip host yang digunakan
  host_port = params["host_port"] # menyimpan informasi port host yang digunakan
  username = params["username"] # menyimpan username
  password = params["password"] # menyimpan password
  is_periodic = params["is_periodic"] # menyimpan informasi is_periodic
  if is_periodic == "PERIODIC": # cek is_periodic adalah PERIODIC
    source_database = params["formatted_source_schema"] if params["source_database"] == None else params["source_database"] # menyimpan informasi source_database apabila bukan "PERIODIC" 
    source_schema = params["formatted_source_schema"] # menyimpan informasi formatted_source_schema apabila "PERIODIC"
  else:
    source_database = params["source_schema"] if params["source_database"] == None else params["source_database"] # menyimpan informasi source_database apabila bukan "PERIODIC" 
    source_schema = params["source_schema"] # menyimpan informasi source_schema apabila bukan "PERIODIC"
  try:
    if database_type.upper() == "SQL SERVER": # kondisi ketika tipe database adalah sql server
    # konfigurasi perolehan data sql server
      return True if spark.read.format("jdbc")\
      .option("driver","com.microsoft.sqlserver.jdbc.SQLServerDriver")\
      .option("url","jdbc:sqlserver://{}:{};databaseName={};user={};password={};"\
        .format(host_ip, host_port, source_database, username, password))\
      .option("dbtable","(SELECT NAME FROM [MASTER].SYS.[DATABASES] WHERE NAME = '{}') as tmp".format(source_schema))\
      .load().count() != 0 else False # menampilkan database sql server
    elif database_type.upper() == "MYSQL": # kondisi ketika tipe database adalah MYSQL
    # konfigurasi perolehan data mysql
      return True if spark.read.format("jdbc")\
      .option("driver","com.mysql.jdbc.Driver")\
      .option("url","jdbc:mysql://{}:{}".format(host_ip, host_port))\
      .option("user", username)\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable","(SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE '{}') as tmp".format(source_schema))\
      .load().count() != 0 else False # menampilkan database mysql
    elif database_type.upper() == "POSTGRES": # kondisi ketika tipe database adalah postgresql
    # konfigurasi perolehan data postgresql
      return True if spark.read.format("jdbc")\
      .option("driver","org.postgresql.Driver")\
      .option("url","jdbc:postgresql://{}:{}/{}".format(host_ip, host_port, source_database))\
      .option("user", username )\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable","(SELECT DISTINCT TABLE_SCHEMA FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{}') as tmp".format(source_schema))\
      .load().count() != 0 else False # cek count distinct schema yang berada di database postgresql
    elif database_type.upper() == "DB2": # kondisi ketika tipe database adalah db2
    # konfigurasi perolehan data db2
      return True if spark.read.format("jdbc")\
      .option("driver","com.ibm.db2.jcc.DB2Driver")\
      .option("url","jdbc:db2://{}:{}/{}".format(host_ip, host_port, source_database))\
      .option("user", username )\
      .option("password", password)\
      .option("dbtable","(SELECT DISTINCT TABLE_SCHEMA FROM SYSIBM.TABLES WHERE TABLE_SCHEMA='{}') as tmp".format(source_schema))\
      .load().count() != 0 else False # cek count distinct schema yang berada di database db2
  except:
    return False
# 28 ==================================================================================================================================================================================================
# edit disini untuk menambankan database baru (sudah ditambah postgress dan db2)
def is_source_table_exist(spark, params):
  """ Cek tabel yang tersedia
 
 Parameter :
  Spark  : objek SparkSession
  params : parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
 
 Return :
  Menampilkan tabel yang tersedia
 """
  database_type = params["database_type"] # menyimpan informasi database yang digunakan
  host_ip = params["host_ip"] # menyimpan informasi ip host yang digunakan
  host_port = params["host_port"] # menyimpan informasi port host yang digunakan
  username = params["username"] # menyimpan username
  password = params["password"] # menyimpan password
  is_periodic = params["is_periodic"] # menyimpan informasi is_periodic
  if is_periodic == "PERIODIC": # cek is_periodic adalah PERIODIC
    source_database = params["formatted_source_schema"] if params["source_database"] == None else params["source_database"] # menyimpan informasi source_database apabila bukan "PERIODIC" 
    source_schema = params["formatted_source_schema"] # menyimpan informasi formatted_source_schema apabila "PERIODIC"
    source_table = params["formatted_source_table"] # menyimpan informasi formatted_source_tabel apabila "PERIODIC"
  else:
    source_database = params["source_schema"] if params["source_database"] == None else params["source_database"] # menyimpan informasi source_database apabila bukan "PERIODIC" 
    source_schema = params["source_schema"] # menyimpan informasi source_schema apabila bukan "PERIODIC"
    source_table = params["source_table"] # menyimpan informasi source_tabel apabila bukan "PERIODIC"
  try:
    if database_type.upper() == "SQL SERVER": # kondisi ketika tipe database adalah sql server
      return True if spark.read.format("jdbc")\
      .option("driver","com.microsoft.sqlserver.jdbc.SQLServerDriver")\
      .option("url","jdbc:sqlserver://{}:{};databaseName={};user={};password={};"\
        .format(host_ip, host_port, source_database, username, password))\
      .option("dbtable","(SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='{}' and TABLE_SCHEMA='dbo') as tmp".format(source_table))\
      .load().count() != 0 else False # cek count tabel yang berada di database sql server
    elif database_type.upper() == "MYSQL": # kondisi ketika tipe database adalah mysql
      return True if spark.read.format("jdbc")\
      .option("driver","com.mysql.jdbc.Driver")\
      .option("url","jdbc:mysql://{}:{}/{}".format(host_ip, host_port, source_schema))\
      .option("user", username )\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable","(SELECT table_name FROM information_schema.tables WHERE table_name LIKE '{}') as tmp".format(source_table))\
      .load().count() != 0 else False # cek count tabel yang berada di database mysql
    elif database_type.upper() == "POSTGRES": # kondisi ketika tipe database adalah postgresql
      return True if spark.read.format("jdbc")\
      .option("driver","org.postgresql.Driver")\
      .option("url","jdbc:postgresql://{}:{}/{}".format(host_ip, host_port, source_database))\
      .option("user", username )\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable","(SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='{}' AND TABLE_SCHEMA='{}') as tmp".format(source_table, source_schema))\
      .load().count() != 0 else False # cek count tabel yang berada di database postgresql
    elif database_type.upper() == "DB2": # kondisi ketika tipe database adalah db2
      return True if spark.read.format("jdbc")\
      .option("driver","com.ibm.db2.jcc.DB2Driver")\
      .option("url","jdbc:db2://{}:{}/{}".format(host_ip, host_port, source_database))\
      .option("user", username )\
      .option("password", password)\
      .option("useSSL", "false")\
      .option("dbtable","(SELECT TABLE_NAME FROM SYSIBM.TABLES WHERE TABLE_NAME='{}' AND TABLE_SCHEMA='{}') as tmp".format(source_table, source_schema))\
      .load().count() != 0 else False # cek count tabel yang berada di database db2
  except:
    return False
# 29 ==================================================================================================================================================================================================
def set_column_delimiter(df):
  """Mengganti space pada kolom dengan '_'
  
  Parameter:
      df: Spark DataFrame input
  
  Return:
      df: Spark DataFrame setelah di-update
  """
  # melakukan perulangan untuk memeriksa setiap kolom
  for col in df.columns: # perulangan seluruh item pada list
    if " " in col: # kondisi ketika kolom memiliki space
      df = df.withColumnRenamed(col, col.replace(" ","_")) # update kolom yang memiliki space
  return df # return Spark DataFrame yang telah ter-update
# 30 ==================================================================================================================================================================================================
def set_column_rename(df, params):
  """Rename kolom yang telah ditentukan
  
  Parameter:
      df: Spark DataFrame input
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
  
  Return:
      df: Spark DataFrame setelah di-update
  """
  hive_rename_col = params["hive_rename_col"] # menimpan variabel hive_rename_col
  
  # melakukan kondisional hive_rename_col tidak kosong
  if hive_rename_col != None and hive_rename_col.strip() != "": # kondisi ketika hive_rename_col tidak kosong
    hive_rename_col = hive_rename_col.split("|") # proses memecah hive_rename_col menjadai list
    
    i=0 # mendefinisikan variabel pencacah
    while i<len(hive_rename_col): # perulangan ketika pencacah lebih kecil dari panjang list
      col_name = hive_rename_col[i].split(":") # proses memecah hive_rename_col menjadai list berisi kolom dan rename kolom
      df = df.withColumnRenamed(col_name[0], col_name[1]) # update nama kolom menjadi nama yang ditentukan
      i+=1 # menambahkan 1 pada pencacah
  return df # return Spark DataFrame yang telah ter-update
# 31 ==================================================================================================================================================================================================
def set_datetime():
  """Mendapatkan tanggal waktu terkini
    
  Return:
      datetime.datetime: representasi tanggal waktu terkini
  """
  return datetime.now(timezone("Asia/Jakarta")) # return datetime.datetime terkini dengan zona waktu "Asia/Jakarta"
# 32 ==================================================================================================================================================================================================
def set_ingest_timer():
  """Mendapatkan waktu terkini dalam bentuk detik
    
  Return:
      float: representasi detik dengan tipe float
  """
  return time() # return time.time untuk memperoleh waktu terkini dalam bentuk detik 
# 33 ==================================================================================================================================================================================================
def update_additional_attributes(spark, params):
  """Update value dari params untuk kelengkapan log activity dan metadata info
  
  Parameters:
      spark: objek SparkSession
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      
  Return:
      dictionaries: hasil proses update value dari parameter input params
  """
  is_periodic = params["is_periodic"] # menyimpan keterangan apakah job periodic atau non periodic
  activity = "INGESTION" # variabel aktifitas yang dilakukan
  activity_desc = str(activity+" "+is_periodic) # membuat variabel deskripsi aktifitas yang dilakukan
  status = params["status"] # menyimpan status job (SUCCESSFUL/FAILURE)
  status_desc = params["status_desc"] # menyimpan deskripsi dari status
  curr_datetime = set_datetime() # mendapatkan tanggal waktu terkini
  params["activity"] = activity # update value params activity
  params["activity_desc"] = get_formatted_string(activity_desc) # update value params activity_desc dengan string yang telah terformat Clavitalize Each Word
  
  # melakukan kondisional sesuai status job
  if status == "FAILURE": # kondisi ketika status job failure
    params["status_desc"] = str("ERROR"+status_desc) # update value status_desc dengan pesan error
  else: # kondisi ketika status job successful
    params["status_desc"] = get_formatted_string(str(status+" "+activity_desc)) # update value params status_desc dengan string yang telah terformat Clavitalize Each Word
  params["dttm_ingest"] = curr_datetime # update value params dttm_ingest dengan tanggal waktu terkini
  params["ds"] = (str(curr_datetime.year) + str(curr_datetime.month).zfill(2) + str(curr_datetime.day).zfill(2)) # update value params ds dengan format yyyyMMdd dari tanggal waktu terkini
  
  # penanganan error dalam memperoleh parameter-parameter lain
  #try:
  params["user_ingestion"] = get_username() # update value dengan username hadoop sesuai user login
  params["job_period"] = get_job_period(params) # update value sesuai keluaran dari fungsi
  first_partition = get_partition(spark, params, True) # mendapatkan partisi awal dari tabel target
  params["first_partition"] = first_partition["partition"] if first_partition != None else None # update value dengan value partisi awal jika ada (None jika tidak ada)
  last_partition = get_partition(spark, params) # mendapatkan partisi akhir dari tabel target
  params["last_partition"] = last_partition["partition"] if last_partition != None else None # update value dengan value partisi akhir jika ada (None jika tidak ada)
  params["file_size"] = get_file_size(spark, params) # update value dengan ukuran keseluruhan tabel target dalam satuan bytes
  params["partition_size"] = get_file_size(spark, params, True) # update value dengan ukuran partisi terakhir tabel target dalam satuan bytes
  params["last_date_ingest"] = get_last_date_ingest(spark, params) # update value dengan tanggal waktu ingest terakhir
  params["storage_path"] = get_describe_formatted(spark, params, "Location") # update value dengan informasi metadata lokasi tabel target
  params["created_date"] = get_describe_formatted(spark, params, "Created") # update value dengan informasi metadata tanggal waktu tabel target pertama kali dibuat
  params["created_by"] = get_describe_formatted(spark, params, "Owner") # update value dengan informasi metadata pembuat tabel target
  
  # melakukan kondisional tabel target memiliki partisi ingest atau tidak
  if params["hive_partition_date"] != None: # kondisi ketika tabel target memiliki partisi terakhir
    partition_date = params["hive_partition_date"].split("|") # membuat list hive_partition_date
    partition_col = params["hive_partition_col"].split("|") # membuat list hive_partition_date
    params["partition_ingest"] = "/".join(["{}={}".format(partition_col[i], partition_date[i]) for i in range(len(partition_date))]) # membuat parameter partition_ingest dari partition_date dan partition_col
    params["partition_path"] = try_or(lambda: params["storage_path"] + "/" + params["partition_ingest"]) # menetapkan lokasi partisi ter-ingest di hive direktori
  else: # kondisi ketika tabel target tidak memiliki partisi terakhir
    params["partition_path"] = params["storage_path"] # menetapkan lokasi data ter-ingest di hive direktori
  params["total_rows"] = get_total_count(spark, params) # mendapatkan jumlah keseluruhan data dari tabel target
  return params # return params yang telah ter-update
  #except:
  #  return params # return params yang telah ter-update
# 34 ==================================================================================================================================================================================================
def update_schema_table(spark, df, params):
  """Update struktur kolom dari perbedaan struktur kolom pada tabel sumber dan tabel target
  
  Parameters:
      spark: objek SparkSession
      df: Spark Dataframe yang akan di-ingest ke tabel target
      params: parameter-parameter pendukung yang disimpan dalam bentuk dictionaries
      
  Return:
      df: Spark DataFrame yang telah ter-update
  """
  hive_mode = params["strategy"] # menyimpan strategy ingest
  hive_schema = params["hive_schema"] # menyimpan nama hive schema
  hive_table = params["hive_table"] # menyimpan nama hive table
  
  # melakukan kondisional untuk menjalankan proses update struktur kolom yaitu ketika strategy ingest adalah append
  hive_table_exist = spark.sql("SHOW TABLES IN {} LIKE '{}'".format(hive_schema, hive_table)).count()
  if hive_mode.upper() == "APPEND" and hive_table_exist == 1: # kondisi ketika strategy ingest append
    # update ketika terdapat kolom baru pada DataFrame ingest
    df_ref = spark.read.table("{}.{}".format(hive_schema, hive_table)) # read tabel target
    col = {x.upper() for x in df.columns} # membuat list kolom dari tabel ingest
    col_ref = {x.upper() for x in df_ref.columns} # membuat list kolom dari tabel target
    col_new = list(col.difference(col_ref)) # mencari kolom baru pada tabel ingest
    
    # melakukan kondisional untuk melakukan proses update struktur kolom
    if len(col_new) > 0: # kondisi ketika terdapat kolom baru pada tabel ingest
        col_new_dtype = [x for x in df.dtypes if x[0].upper() in col_new] # mendapatkan tipe data dari kolom baru
        query_add = ','.join(["`{}` {}".format(col_new[x].lower(), col_new_dtype[x][1]) for x in range(len(col_new))]) # membuat daftar kolom dan tipenya untuk dilakukan add schema
        query_add = "ALTER TABLE {}.{} ADD COLUMNS ({})".format(hive_schema, hive_table, query_add) # membuat query add columns
        spark.sql(query_add) # menjalankan query add columns
    
    # update ketika terdapat kolom yang hilang dari tabel ingest
    df_ref = spark.read.table("{}.{}".format(hive_schema, hive_table)) # read tabel target
    col_ref = {x.upper() for x in df_ref.columns} # membuat list kolom dari tabel target
    col_missing = list(col_ref.difference(col)) # mencari kolom yang hilang pada tabel ingest
    
    # melakukan kondisional untuk melakukan proses update struktur kolom
    if len(col_missing) > 0: # kondisi ketika terdapat kolom hilang pada tabel ingest
      col_missing_dtype = [x for x in df_ref.dtypes if x[0].upper() in col_missing] # mendapatkan tipe data dari kolom yang hilang
      # melakukan perulangan untuk update kolom tabel ingest
      for i in col_missing_dtype: # perulangan sebanyak kolom yang hilang
        df = df.withColumn(i[0], F.lit(None).cast(i[1])) # menambahkan kolom yang hilang dengan nilai None
    df = df.select(df_ref.columns) # menyesuaikan susunan kolom tabel ingest
    
    # update tipe data kolom sesuai dengan tabel target
    dtype = df.dtypes # mendapatkan kolom dan tipe dari tabel ingest
    # melakukan perulangan untuk update tipe data
    for i, dt in enumerate(df_ref.dtypes): # perulangan sebanyak kolom dari tabel target
      # melakukan kondisional untuk memeriksa perbedaan tipe data
      if dt[1] != dtype[i][1]: # kondisi ketika tipe kolom dari tabel ingest dan tabel target berbeda
        df = df.withColumn(dtype[i][0],F.col(dtype[i][0]).cast(dt[1])) # update tipe data kolom pada tabel ingest
  return df # return Spark DataFrame dengan struktur kolom yang telah ter-update
# 35 ==================================================================================================================================================================================================

