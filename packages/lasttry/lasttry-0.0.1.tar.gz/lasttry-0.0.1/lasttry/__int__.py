def pro6():
    print("""!pip install pyspark
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MovieRatingsAnalysis").getOrCreate()

movies_df = spark.read.csv("/content/movies.csv", header=True, inferSchema=True)
ratings_df = spark.read.csv("/content/ratings.csv", header=True, inferSchema=True)

movies_rdd = movies_df.rdd
ratings_rdd = ratings_df.rdd

avg_ratings_rdd = ratings_rdd.map(lambda x: (x['movieId'], (x['rating'], 1))) \
    .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1])) \
    .mapValues(lambda x: x[0] / x[1])

lowest_avg_rating = avg_ratings_rdd.sortBy(lambda x: x[1]).first()
print(f"Movie with the lowest average rating: {lowest_avg_rating}")

from pyspark.sql.functions import from_unixtime, year, month

ratings_df = ratings_df.withColumn("year", year(from_unixtime(ratings_df['timestamp']))) \
                       .withColumn("month", month(from_unixtime(ratings_df['timestamp'])))

ratings_over_time = ratings_df.groupBy("year", "month").count().orderBy("year", "month")
ratings_over_time.show()

user_ratings_count = ratings_rdd.map(lambda x: (x['userId'], 1)) \
    .reduceByKey(lambda x, y: x + y) \
    .sortBy(lambda x: x[1], ascending=False)

top_users = user_ratings_count.take(10)
print(f"Top users by number of ratings: {top_users}")

movie_ratings_stats = ratings_rdd.map(lambda x: (x['movieId'], (x['rating'], 1))) \
    .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1])) \
    .mapValues(lambda x: (x[0] / x[1], x[1]))

min_ratings = 100
qualified_movies = movie_ratings_stats.filter(lambda x: x[1][1] >= min_ratings)
highest_rated_movies = qualified_movies.sortBy(lambda x: x[1][0], ascending=False).take(10)
print(f"Highest-rated movies with at least {min_ratings} ratings: {highest_rated_movies}")
""")
def pro7():
    print("""import pyspark
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('housing_price_model').getOrCreate()

df = spark.read.csv('/content/cruise_ship.csv', inferSchema=True, header=True)
df.show(10)
df.printSchema()
df.columns

from pyspark.ml.feature import StringIndexer
indexer = StringIndexer(inputCol='Cruise_line', outputCol='cruise_cat')
indexed = indexer.fit(df).transform(df)

from pyspark.ml.feature import VectorAssembler
assembler = VectorAssembler(inputCols=['Age',
 'Tonnage',
 'passengers',
 'length',
 'cabins',
 'passenger_density',
 'cruise_cat'], outputCol='features')
output = assembler.transform(indexed)
output.select('features', 'crew').show(5)

final_data = output.select('features', 'crew')
train_data, test_data = final_data.randomSplit([0.7, 0.3])

from pyspark.ml.regression import LinearRegression
ship_lr = LinearRegression(featuresCol='features', labelCol='crew')
ship_lr = ship_lr.fit(train_data)

pred = ship_lr.evaluate(test_data)
pred.predictions.show()
""")
def pro3():
    print("""import sys
for line in sys.stdin:
    val =  line.strip()
    year , temp = val[0:4], val[5:9]
    if temp != "9999":
        print("%s\\t%s" % (year,temp))

import sys

last_key, max_val = None, 0

for line in sys.stdin:
    key, val = line.strip().split("\\t")

    if last_key and last_key != key:
        print("%s\\t%s" % (last_key, max_val))
        last_key, max_val = key, float(val)
    else:
        last_key, max_val = key, max(max_val, float(val))

if last_key:
    print("%s\\t%s" % (last_key, max_val))
""")
    
def pro2():
    print("""import sys

for line in sys.stdin:
    line = line.strip()
    words = line.split()
    for word in words:
        print('%s\\t%s' % (word, 1))

import sys

current_word = None
current_count = 0
word = None

for line in sys.stdin:
    line = line.strip()
    word, count = line.split('\\t', 1)
    try:
        count = int(count)
    except ValueError:
        continue

    if current_word == word:
        current_count += count
    else:
        if current_word:
            print('%s\\t%s' % (current_word, current_count))
        current_count = count
        current_word = word

if current_word == word:
    print('%s\\t%s' % (current_word, current_count))
""")
