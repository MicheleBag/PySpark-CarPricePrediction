
import pyspark
from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col,isnan,when,count
from pyspark.ml import Pipeline
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler, MinMaxScaler, StringIndexer, OneHotEncoder
from pyspark2pmml import PMMLBuilder
from pyspark2pmml import toPMMLBytes



#SparkSession is now the entry point of Spark
#SparkSession can also be construed as gateway to spark libraries
#create instance of spark class
spark=SparkSession.builder.appName('UsedCarPrice').getOrCreate()
sc = spark.sparkContext

#create spark dataframe of input csv file
path = 'hdfs://localhost:9000/user/bigdata/input'
df=spark.read.csv(path + '/dataset.csv'
                  ,inferSchema=True,header=True)

df.show(10)

# Removing useless carID feature
df = df.drop('carID')

# Checking for NaN values
check_nan = df.select([count(when(col(c).contains('None') |                             col(c).contains('NULL') |                             (col(c) == '' ) |                             col(c).isNull() |                             isnan(c), c 
                           )).alias(c)
                    for c in df.columns])
check_nan.show()

# Features to be normalized or one-hot-encoded
numerical_features = ['year', 'mileage','tax','mpg', 'engineSize']
categorical_features = ['brand', 'model', 'transmission', 'fuelType']

# (MLlib works only with one column vector)
# assembler combines a given list of columns into a single vector column
assembler = VectorAssembler(inputCols=numerical_features, outputCol="features_to_scale")

# Normalizing features
scaler = MinMaxScaler(inputCol="features_to_scale", outputCol="features_scaled")

# Spark MLlib expects every value to be in numeric form
# using StringIndexer, string type will be typecast to numeric datatype
indexer=[StringIndexer(inputCol=column, outputCol=column+"_cat").fit(df) for column in categorical_features]

# One-hot-encoder for indexed categorical features
ohe = OneHotEncoder(inputCols = [col+'_cat' for col in categorical_features], 
                    outputCols=[col+'_ohe' for col in categorical_features])

# Final assembler for the ohe columns and the normalized features already vectorized
input = [col+'_ohe' for col in categorical_features]
input.append('features_scaled')
final_assembler = VectorAssembler(inputCols=input,outputCol="features")

# Linear Regression
regressor = LinearRegression(labelCol="price",featuresCol="features", regParam=0.1)

# Inizializing pipeline
stages = indexer
stages.append(assembler)
stages.append(scaler)
stages.append(ohe)
stages.append(final_assembler)
stages.append(regressor)
pipeline = Pipeline().setStages(stages)

# Splitting dataset in train&test
train_set, test_set=df.randomSplit([0.7,0.3])

# Model training
pipeline_model = pipeline.fit(train_set)

# Make predictions
predictions = pipeline_model.transform(test_set)

# Show 10 example rows
predictions.select("prediction", "price", "features").show(10)
eval = RegressionEvaluator(labelCol="price", predictionCol="prediction", metricName="r2")
# R2
r2 = eval.evaluate(predictions, {eval.metricName: "r2"})
print("r2: %.3f" %r2)

# Training pipeline model with entire dataset
pipeline_model = pipeline.fit(df)

# Exporting pmml to hdfs
pmmlBuilder = PMMLBuilder(sc, df, pipeline_model).buildByteArray()
output = sc.parallelize([pmmlBuilder])
output.saveAsTextFile("hdfs://localhost:9000/user/bigdata/output")

sc.stop()





