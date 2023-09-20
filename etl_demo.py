# This structure was copy pasted from Appendix on https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html

import sys
from awsglue.transforms import *
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import re

from awsglue.utils import getResolvedOptions


class GluePythonSampleTest:
    def __init__(self):
        params = []
        if '--JOB_NAME' in sys.argv:
            params.append('JOB_NAME')
        args = getResolvedOptions(sys.argv, params)

        self.spark_context = SparkContext.getOrCreate()
        self.glue_context = GlueContext(self.spark_context)
        self.job = Job(self.glue_context)

        if 'JOB_NAME' in args:
            jobname = args['JOB_NAME']
        else:
            jobname = "test"
        self.job.init(jobname, args)

    def run(self):
        dyf = read_file(self.glue_context, self.spark_context, 'file:///local/to/all/data.csv')
        dyf.printSchema()

        dyf_fixed_schema = ApplyMapping.apply(
            frame=dyf,
            mappings=[
                ("id", "string", "id", "string"),
                ("created_at", "string", "created_at", "timestamp"),
                ("parameter", "string", "parameter", "string"),
                ("serial_number", "string", "serial_number", "string"),
                ("ts", "string", "ts", "timestamp"),
                ("value", "string", "value", "double"),
                ("device_model_id", "string", "device_model_id", "string"),
            ],
            transformation_ctx="fixedSchema",
        )

        dyf_fixed_schema.printSchema()

        
        filter_output_energy = Filter.apply(
            frame=dyf_fixed_schema,
            f=lambda row: (bool(re.match("outputEnergy", row["parameter"]))),
            transformation_ctx="filter_output_energy",
        )

        print("filtered values")
        filter_output_energy.show()


        write_file(filter_output_energy, 'file:///local/to/all/data_processed/')

        self.job.commit()


def read_file(glue_context, spark_context, path):

    spark = glue_context.spark_session

    #reads a file with spark
    dataFrame = spark.read.option("header",True).option("delimiter", ",").csv(path)
    dataFrame.show()
    dataFrame.printSchema()


    #converts to a "DynamicDataFrame", we could also use DynamicDataFrame.fromDF, but
    #this way makes it more similar to the standard way to access data on glue.
    dynamic_frame = glue_context.create_dynamic_frame_from_rdd(
        data=dataFrame.rdd,
        name="teste",
        schema=dataFrame.schema,
        transformation_ctx="your_transform_ctx"
    )


    return dynamic_frame

def write_file(dynamic_frame, path):

    sparkDf = dynamic_frame.toDF()
    #writes the file back with spark
    #this is very differently handled in glue using a data sink, however we cant
    #use it here, unless we use S3.
    sparkDf.write.option("header", True).csv(path)





if __name__ == '__main__':
    GluePythonSampleTest().run()
