#=============================================================#
###  CREATED AT     : 04 MARET 2024                         ###
###  UPDATED AT     : 17 JULI 2024                          ###
###  COPYRIGHT      : ANDRI ARIYANTO                        ###
###  DESCRIPTION    : Module untuk melakukan load data      ###
#=============================================================#

## HDFS ==============================================================================================

def load_to_hive(spark, df, schema, table, partition=None, mode="append", repartition_number=None, blocksize=256):
  """Melakukan penulisan pyspark dataframe sebagai tabel hive di hdfs
  
  Args:
      spark (pyspark.sql.session.SparkSession): spark session
      df (pyspark.sql.dataframe.DataFrame): pyspark dataframe yang akan di tulis sebagai tabel hive
      schema (str): target schema di hdfs
      table (str): target table di hdfs
      partition (str): kolom yang akan dijadikan partisi (dipisahkan ',' jika lebih dari satu kolom)
          (default is None)
      mode (str): cara yang dilakukan untuk penulisan tabel
          (optional is append, overwrite, error, ignore)
          (default is append)
      repartition_number (int): jumlah file parquet yang diinginkan dalam satu partisi
          (default is None)      
      blocksize (int): ukuran per file dalam satuan megabyte
          (default is 256)
    
  Returns:
      -
  """
  
  if schema.startswith("dev"):
    hdfs_path = "/dev/"
  else:
    hdfs_path = "/user/hive/warehouse/"
  
  print("Write table to Hive: {0}.{1}".format(schema, table))
    
  # pengecekan partitioned table
  if partition:
    
    # kondisi ketika tabel berpartisi
    partition = partition.split(",")
    list_partition = df.select(partition).distinct().collect()
    
    unit = len(str(len(list_partition)))
    
    first = True
    row_total = 0
    
    # loop untuk penulisan data per partisi sesuai standard blocksize
    for i, row in enumerate(list_partition):
      
      condition = ' AND '.join(["{0}='{1}'".format(col, row[col]) for col in partition])
      df_write = df.filter(condition)


      if not repartition_number:
        tag = '_'.join([row[col].strip() for col in partition]).lower()

        spark.sql("DROP TABLE IF EXISTS project_sv.{0}_{1}_allow_deleted".format(table, tag))

        # penulisan sample data untuk estimasi ukuran data
        df_write\
          .sample(False,0.1,None)\
          .write\
          .format("parquet")\
          .mode("overwrite")\
          .saveAsTable("project_sv.{0}_{1}_allow_deleted".format(table, tag))

        # mendapatkan metadata content summary dari sample table
        path = lambda p: spark._jvm.org.apache.hadoop.fs.Path(p)
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
        hdfs_folder = fs.getContentSummary(path(hdfs_path+"project_sv.db/{0}_{1}_allow_deleted/".format(table, tag)))

        # kalkulasi jumlah file yang optimal sesuai standard blocksize
        blocksize_number = float(hdfs_folder.getLength()*10)/float(blocksize*1024*1024)
        repartition_number = int(1 if blocksize_number < 1 else blocksize_number)

        spark.sql("DROP TABLE project_sv.{0}_{1}_allow_deleted".format(table, tag))

      # set jumlah file sesuai hasil kalkulasi
      df_write = df_write.repartition(repartition_number)
    
      # penghapusan data partisi jika sudah ada di target tabel
      if spark.sql("SHOW TABLES IN {0} LIKE '{1}'".format(schema, table)).count() != 0:
        query_drop_partition = "ALTER TABLE {0}.{1} DROP IF EXISTS PARTITION({2})".format(schema, table, condition.replace(" AND ",","))
        spark.sql(query_drop_partition) # menghapus partisi di spark

      # penulisan pyspark dataframe ke hdfs
      df_write\
        .write\
        .format("parquet")\
        .partitionBy(partition)\
        .mode(mode)\
        .saveAsTable("{0}.{1}".format(schema,table))

      spark.sql("MSCK REPAIR TABLE {0}.{1}".format(schema, table)) # memperbaiki tabel
      spark.sql("ANALYZE TABLE {0}.{1} PARTITION ({2}) COMPUTE STATISTICS".format(schema, table, condition.replace(" AND ",","))) # kalkulasi data
      spark.sql("REFRESH TABLE {0}.{1}".format(schema, table)) # refresh tabel di spark
      

      first = False
      if not first: mode="append"
        
      row_count = df_write.count()
      row_total += row_count
      print("{0}) Count Record ({1}) = {2}".format(str(i+1).ljust(unit, " "), condition.replace(" AND ",","), row_count))

  else:
    
    if not repartition_number:
      # kondisi ketika tabel berpartisi    
      spark.sql("DROP TABLE IF EXISTS project_sv.{0}_allow_deleted".format(table))

      # penulisan sample data untuk estimasi ukuran data
      df\
        .sample(False,0.1,None)\
        .write\
        .format("parquet")\
        .mode("overwrite")\
        .saveAsTable("project_sv.{0}_allow_deleted".format(table))

      # mendapatkan metadata content summary dari sample table
      path = lambda p: spark._jvm.org.apache.hadoop.fs.Path(p)
      fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(spark._jsc.hadoopConfiguration())
      hdfs_folder = fs.getContentSummary(path(hdfs_path+"project_sv.db/{0}_allow_deleted/".format(table)))

      # kalkulasi jumlah file yang optimal sesuai standard blocksize
      blocksize_number = float(hdfs_folder.getLength()*10)/float(blocksize*1024*1024)
      repartition_number = int(1 if blocksize_number < 1 else blocksize_number)

      spark.sql("DROP TABLE project_sv.{0}_allow_deleted".format(table))

    # set jumlah file sesuai hasil kalkulasi
    df = df.repartition(repartition_number)

    # penulisan pyspark dataframe ke hdfs
    df\
      .write\
      .format("parquet")\
      .mode(mode)\
      .saveAsTable("{0}.{1}".format(schema,table))

    spark.sql("ANALYZE TABLE {0}.{1} COMPUTE STATISTICS".format(schema, table)) # kalkulasi data
    spark.sql("REFRESH TABLE {0}.{1}".format(schema, table)) # refresh tabel di spark
    

  print("\n====>> Grand Total Record =", df.count())
  
  
  
  
  
  
  
  
## POSTGRESQL ========================================================================================
  
import psycopg2


def postgresql_execute_command(database, ip, port, username, password, query):
  """Menjalankan query di postgresql
  
  Args:
      database (str): target database di posgresql
      ip (str): target ip di posgresql
      port (str): target port di posgresql
      username (str): username di posgresql
      password (str): password di posgresql
      query (str): query yang akan di eksekusi
    
  Returns:
      -
  """
  
  # make a new connection
  conn = psycopg2.connect(
    host=ip,
    port=port,
    database=database,
    user=username,
    password=password
  )

  cur = conn.cursor()  # creating a cursor

  # executing queries
  cur.execute(query)

  # commit the changes
  conn.commit() # This right here

  # close connection
  cur.close()
  conn.close()

  
def postgresql_execute_fetchall(database, ip, port, username, password, query):
  """Menjalankan query di postgresql
  
  Args:
      database (str): target database di posgresql
      ip (str): target ip di posgresql
      port (str): target port di posgresql
      username (str): username di posgresql
      password (str): password di posgresql
      query (str): query yang akan di eksekusi
    
  Returns:
      list: data keluaran dari query yang di eksekusi
  """
  
  # make a new connection
  conn = psycopg2.connect(
    host=ip,
    port=port,
    database=database,
    user=username,
    password=password
  )
  cur = conn.cursor()  # creating a cursor

  # executing queries
  cur.execute(query)

  # get response data
  result = cur.fetchall()

  # close connection
  cur.close()
  conn.close()

  return result
  
  
def postgresql_drop_table(database, schema, table, ip, port, username, password):
  """Melakukan query drop table di postgresql
  
  Args:
      database (str): target database di posgresql
      schema (str): target schema di posgresql yang akan di hapus
      table (str): target table di posgresql yang akan di hapus
      ip (str): target ip di posgresql
      port (str): target port di posgresql
      username (str): username di posgresql
      password (str): password di posgresql
    
  Returns:
      -
  """
  
  # pembentukan query drop table
  query = "DROP TABLE IF EXISTS {}.{}".format(schema, table)
  
  # eksekusi query drop table
  postgresql_execute_command(database, ip, port, username, password, query)
     
    
def postgresql_truncate_table(database, schema, table, ip, port, username, password):
  """Melakukan query truncate table di postgresql
  
  Args:
      database (str): target database di posgresql
      schema (str): target schema di posgresql yang akan di truncate
      table (str): target table di posgresql yang akan di truncate
      ip (str): target ip di posgresql
      port (str): target port di posgresql
      username (str): username di posgresql
      password (str): password di posgresql
    
  Returns:
      -
  """
  
  # query truncate table
  query = "TRUNCATE TABLE {}.{}".format(schema, table)
  
  # eksekusi query truncate table
  postgresql_execute_command(database, ip, port, username, password, query)
  
  
def load_to_postgresql(df, database, schema, table, ip, port, username, password, mode="append", strategy=None, ddl=None):
  """Melakukan penulisan pyspark dataframe sebagai tabel di postgresql
  
  Args:
      df (pyspark.sql.dataframe.DataFrame): pyspark dataframe yang akan di tulis sebagai tabel posgresql
      database (str): target database di posgresql
      schema (str): target schema di posgresql
      table (str): target table di posgresql
      ip (str): target ip di posgresql
      port (str): target port di posgresql
      username (str): username di posgresql
      password (str): password di posgresql
      mode (str): cara yang dilakukan untuk penulisan tabel
          (optional is append, overwrite, error, ignore)
          (default is append)
      strategy (str): proses yang dilakukan sebelum penulisan tabel
          (optional is None, truncate, drop)
          (default is None)
      ddl (str): query create untuk melakukan pembuatan struktur tabel
          (default is None)
    
  Returns:
      -
  """
  
  print("Write table to PostgreSQL: {}.{}".format(schema, table))
    
  if strategy:
    
    if strategy.lower() == "truncate":
      # menjalankan query truncate table
      postgresql_truncate_table(database, schema, table, ip, port, username, password)
    elif strategy.lower() == "drop":
      # menjalankan query drop table
      postgresql_drop_table(database, schema, table, ip, port, username, password)
      
  if ddl:
    # menjalankan query dll
    postgresql_execute_command(database, ip, port, username, password, ddl)
    
  # penulisan pyspark dataframe ke postgresql
  df\
    .write\
    .mode(mode)\
    .format("jdbc")\
    .option("driver", "org.postgresql.Driver")\
    .option("url", "jdbc:postgresql://{}:{}/{}".format(ip, port, database))\
    .option("user", username)\
    .option("password", password)\
    .option("dbtable", ".".join([schema, table]))\
    .save()
    
  print("\n====>> Total Record =", df.count())
    
    
    
    
    
    
    
    
    
    
## MYSQL =============================================================================================

import mysql.connector as ms


def mysql_execute_command(schema, ip, port, username, password, query):
  """Menjalankan query di mysql
  
  Args:
      schema (str): target schema di mysql
      ip (str): target ip di mysql
      port (str): target port di mysql
      username (str): username di mysql
      password (str): password di mysql
      query (str): query yang akan di eksekusi
    
  Returns:
      -
  """
  # make a new connection  
  conn = ms.connect(
    host=ip,
    port=port,
    database=schema,
    user=username,
    password=password
  )

  cur = conn.cursor() # creating a cursor

  # executing queries
  cur.execute(query)

  # commit the changes
  conn.commit() # This right here

  # close connection
  cur.close()
  conn.close()

  
def mysql_execute_fetchall(schema, ip, port, username, password, query):
  """Menjalankan query di mysql
  
  Args:
      schema (str): target schema di mysql
      ip (str): target ip di mysql
      port (str): target port di mysql
      username (str): username di mysql
      password (str): password di mysql
      query (str): query yang akan di eksekusi
    
  Returns:
      list: data keluaran dari query yang di eksekusi
  """
  
  # make a new connection
  conn = ms.connect(
    host=ip,
    port=port,
    database=schema,
    user=username,
    password=password
  )

  cur = conn.cursor() # creating a cursor

  # executing queries
  cur.execute(query)

  # get response data
  result = cur.fetchall()

  # close connection
  cur.close()
  conn.close()

  return result


  
def mysql_drop_table(schema, table, ip, port, username, password):
  """Melakukan query drop table di mysql
  
  Args:
      schema (str): target schema di mysql yang akan di hapus
      table (str): target table di mysql yang akan di hapus
      ip (str): target ip di mysql
      port (str): target port di mysql
      username (str): username di mysql
      password (str): password di mysql
    
  Returns:
      -
  """
  
  # pembentukan query drop table  
  query = "DROP TABLE IF EXISTS {}.{}".format(schema, table)
  
  # eksekusi query drop table
  mysql_execute_command(schema, ip, port, username, password, query)
        
def mysql_truncate_table(schema, table, ip, port, username, password):
  """Melakukan query truncate table di mysql
  
  Args:
      schema (str): target schema di mysql yang akan di truncate
      table (str): target table di mysql yang akan di truncate
      ip (str): target ip di mysql
      port (str): target port di mysql
      username (str): username di mysql
      password (str): password di mysql
    
  Returns:
      -
  """
  
  # pembentukan query truncate table
  query = "TRUNCATE TABLE {}.{}".format(schema, table)
  
  # eksekusi query truncate table
  mysql_execute_command(schema, ip, port, username, password, query)
  
def load_to_mysql(df, schema, table, ip, port, username, password, mode="append", strategy=None, ddl=None):
  """Melakukan penulisan pyspark dataframe sebagai tabel di mysql
  
  Args:
      df (pyspark.sql.dataframe.DataFrame): pyspark dataframe yang akan di tulis sebagai tabel mysql
      schema (str): target schema di mysql
      table (str): target table di mysql
      ip (str): target ip di mysql
      port (str): target port di mysql
      username (str): username di mysql
      password (str): password di mysql
      mode (str): cara yang dilakukan untuk penulisan tabel
          (optional is append, overwrite, error, ignore)
          (default is append)
      strategy (str): proses yang dilakukan sebelum penulisan tabel
          (optional is None, truncate, drop)
          (default is None)
      ddl (str): query create untuk melakukan pembuatan struktur tabel
          (default is None)
    
  Returns:
      -
  """
      
  if strategy:
    
    if strategy.lower() == "truncate":
      # menjalankan query truncate table
      mysql_truncate_table(schema, table, ip, port, username, password)
    elif strategy.lower() == "drop":
      # menjalankan query drop table
      mysql_drop_table(schema, table, ip, port, username, password)
      
  if ddl:
    # menjalankan query dll
    mysql_execute_command(schema, ip, port, username, password, ddl)
    
  # penulisan pyspark dataframe ke mysql    
  df\
    .write\
    .mode(mode)\
    .format("jdbc")\
    .option("driver", "com.mysql.cj.jdbc.Driver")\
    .option("url","jdbc:mysql://"+ip+":"+port+"/"+schema+"?user="+username+"&password="+password+"&characterEncoding=UTF-8&connectionCollation=utf8mb4_unicode_ci&useUnicode=yes&serverTimezone=Asia%2FJakarta&sessionVariables=character_set_server%3Dutf8mb4,character_set_client%3Dutf8mb4,character_set_connection%3Dutf8mb4,character_set_results%3Dutf8mb4,collation_connection%3Dutf8mb4_unicode_ci")\
    .option("useSSL", "false")\
    .option("dbtable", ".".join([schema, table]))\
    .save()
  
  print("\n====>> Total Record =", df.count())
