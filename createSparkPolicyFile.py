
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, LongType, DateType, DoubleType, IntegerType, ArrayType, BooleanType
from pyspark.sql.functions import lit, col, max, min, mean, udf, pandas_udf, PandasUDFType
from pyspark.sql.window import Window

import pyarrow
import numpy as np
import pandas as pd
import os
import sys

policySchema = StructType([\
        StructField('cycle',         IntegerType(), True),\
        StructField('turn',          IntegerType(), True),\
        StructField('move',          IntegerType(), True),\
        StructField('state_',        StringType(),  True),\
        StructField('reward',        IntegerType(), True),\
        StructField('action_sparse', StringType(),  True),\
        StructField('action_verbose',StringType(),  True),\
        StructField('action_size',   IntegerType(), True),\
        StructField('done',          IntegerType(), True),\
        StructField('max_reward',    IntegerType(), True),\
        StructField('max_moves',     IntegerType(), True),\
        StructField('move_range',    IntegerType(), True),\
        StructField('value',         DoubleType(),  True)])  

#policySchema = StructType([\
#        StructField('state_', StringType(), True),\
#        StructField('action', StringType(), True),\
#        StructField('value',  DoubleType(), True)])  

spark = SparkSession \
    .builder \
    .appName("policyApp") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

spark.conf.set("spark.dynamicAllocation.enabled", "true")
#spark.conf.set("spark.executor.cores", 8)
#spark.conf.set("spark.executor.memory",'16g')
#spark.conf.set("spark.driver.memory",'128g')
#spark.conf.set("spark.dynamicAllocation.minExecutors",1)
#spark.conf.set("spark.dynamicAllocation.maxExecutors",16)
#spark.conf.set("spark.sql.shuffle.partitions", 16)
#spark.conf.set("conf spark.driver.maxResultSize","2.5g")

infiles      = ["xx00","xx01","xx02","xx03","xx04","xx05","xx06","xx07","xx08"]
#infiles      = ["xaa"]

base_dir     = "/data_data/reinforcement_learning/results/"

for infile_name in infiles:
    try:
        infile   = os.path.join(base_dir,infile_name)
        print("=========================================================================")
        print("Processing file:\t {}".format(infile))
        print("=========================================================================")
        outfile  = infile + ".out"
        policyDF = spark.read\
            .option("sep","\t")\
            .option("header", "false")\
            .schema(policySchema)\
            .csv(infile).drop('max_reward').drop('max_moves').drop('move_range').drop('action_size').drop('action_verbose')

        policyDF.show(5, False)

        policyDF.createOrReplaceTempView("policyView")

        @udf(StringType())
        def string_to_arr(s):
            return str([int(x) for x in s]).replace(" ","")

        print("=========================================================================")
        print("Creating output file:\t{}".format(outfile))
        print("=========================================================================\n")

        w = Window.partitionBy('state', 'turn', 'action')

        policyDF.withColumn('state', string_to_arr(col('state_')))\
            .drop("state_").drop('cycle').drop('move').drop('reward')\
            .select('state', 'turn', 'action_sparse', 'value')\
            .toPandas().to_csv(outfile, sep='\t', index=False, header=False, encoding='utf-8')
        
    except:
        print("No such file:\t{}".format(infile_name))
