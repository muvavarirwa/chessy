
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, StringType, LongType, DateType, DoubleType, IntegerType, ArrayType, BooleanType
from pyspark.sql.functions import lit, col, max, min, udf, mean, last, first, count
from pyspark.sql.window import Window

gameSchema = StructType([\
        StructField('cycle',         IntegerType(), True),\
        StructField('turn',      IntegerType(), True),\
        StructField('move',          IntegerType(), True),\
        StructField('state',         StringType(),  True),\
        StructField('reward',        IntegerType(), True),\
        StructField('action_sparse', StringType(),  True),\
        StructField('action_verbose',StringType(),  True),\
        StructField('action_size',   IntegerType(), True),\
        StructField('done',          IntegerType(), True)])  

spark = SparkSession \
    .builder \
    .appName("StructuredGameEvents") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
spark.conf.set("spark.executor.heartbeatInterval", "2000000") 
spark.conf.set("spark.network.timeout", "3000000")
spark.conf.set("spark.dynamicAllocation.enabled", "true")
spark.conf.set("spark.executor.cores", 8)
spark.conf.set("spark.executor.memory",'16g')
spark.conf.set("spark.driver.memory",'192g')
spark.conf.set("spark.dynamicAllocation.minExecutors",1)
spark.conf.set("spark.dynamicAllocation.maxExecutors",16)
spark.conf.set("spark.sql.shuffle.partitions", 8)
spark.conf.set("conf spark.driver.maxResultSize","92g")

static = spark.read.csv("/data_data/reinforcement_learning/results/output/1.1604238722.691643.tsv")

dataSchema = static.schema

gamesDF = spark.readStream\
    .option("sep","	")\
    .option("header", "false")\
    .schema(gameSchema).csv("/data_data/reinforcement_learning/results/output")

gamesDF.createOrReplaceTempView("gamesView")



def getDiscRewards(turn, reward, max_reward, move_range):
    
    discount    = 0.99
    
    move_reward = -1.0
    
    try:
        max_reward =(max_reward)*(-1)**turn
    except:
        max_reward = 0
    
    interim_reward = sum([move_reward*discount**x for x in range(move_range)])
    
    terminal_reward = max_reward*discount**move_range
    
    total_reward    = interim_reward + terminal_reward
    
    return total_reward


getValue_udf     = udf(lambda turn, reward, max_reward, move_range: getDiscRewards(turn, reward, max_reward, move_range), DoubleType() )

getMoveRange_udf = udf(lambda move, max_moves: int((max_moves - move )/2), IntegerType())

getTurn_udf      = udf(lambda move: int(move % 2), IntegerType())

w = Window.partitionBy('cycle')

def foreach_batch_function(df, epoch_id):
#    df.withColumn("max_reward",last(col("reward")).over(w))\
#    .where("turn == 0")\
#    .withColumn("max_moves", max(col("move")).over(w))\
#    .withColumn("move_range",getMoveRange_udf(col("move"),col("max_moves")))\
#    .withColumn("value",getValue_udf(lit(0), col("reward"),col("max_reward"), col("move_range")))\
#    .coalesce(1)\
#    .write.format('com.databricks.spark.csv')\
#    .mode("append")\
#    .save('/data_data/reinforcement_learning/results/spark_output_0/', sep='\t', index=False, header=False, encoding='utf-8')

   df.withColumn("max_reward",last(col("reward")).over(w))\
   .where("turn == 1")\
   .withColumn("max_moves", max(col("move")).over(w))\
   .withColumn("move_range",getMoveRange_udf(col("move"),col("max_moves")))\
   .withColumn("value",getValue_udf(lit(1), col("reward"),col("max_reward"), col("move_range")))\
   .coalesce(1)\
   .write.format('com.databricks.spark.csv')\
   .mode("append")\
   .save('/data_data/reinforcement_learning/results/spark_output_5/', sep='\t', index=False, header=False, encoding='utf-8')
    
gamesDF.writeStream\
    .option("format", "append")\
    .trigger(processingTime='14400 seconds')\
    .foreachBatch(foreach_batch_function)\
    .start()\
    .awaitTermination()  

