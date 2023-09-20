# Some ~~hate~~fun with local AWS Glue ETL jobs

Extract Transform and Load (ETL) is somewhat a popular concept on data science. The main
idea is to load data, perform some manipulation and output data in different formats.

The popular tool on this topic is [Apache Spark](https://spark.apache.org/) which
is a solid framework to handle super parallel distributed data processing jobs. The Apache
Spark is somewhat derived from [Apache Hadoop](https://hadoop.apache.org/) which is java based library
focused on distributed files and process scheduling.

[Aws Glue](https://aws.amazon.com/glue/?nc1=h_ls), on the other hand, is the Amazon solution
to provide Spark services as, well, a service :). Running Spark on a single machine is not enough trouble
(even though it took me a while), however handling a cluster of Spark nodes to process big batches
of data require ton of additional work, which is where Glue comes in. Using glue extension of spark
we can load and upload data directly from Aws S3, which is the popular choice, even though many other
data sources/sinks are available.

## Enough Talking give me the code! Oh wait

As many know, Spark, and therefore Glue, are integrated in many languages. Here we are using python,
scala is also a good choice given the amout of examples online. A Spark job run the python code to 
process a chunk of data which is distributed using partitions, every job process a partition, the
input usually is sliced into as many partitions as possible or as configured by the user.

The text above means that the Spark itself is more like an engine that will run the code, thus it
needs to be configured first in order to get things done. We can achieve somewhat the same results
by using pure Spark, but since we want to use AWS Glue we need additional configuration. Running glue
on AWS is easy enough, just a few clicks and you are on the visual editor and can run your code,
to run locally AWS suggests the material on this [link](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html)
which made almost no sense in my opinion since it "seems" that you need aws access to run your local
codes.

According the docs, it is possible to run a local ETL Glue Job using either docker or downloading the
libs and running directly into the terminal, however the Docker download was taking forever, so I decided to download the
libraries, however the steps here should work when running on docker as well, maybe with minor changes on docker_run
to include the files to process.

Finally, to overcome the horrible documentation and the ton of noise from the forums I tried to merge some comments
from github, stack overflow, chat gpt, etc... The configuration that follows was 
an adaptation to what is written on [AWS Glue Repo on github](https://github.com/awslabs/aws-glue-libs) to
make it work with local files, also I'm using WSL-2.0, on linux the steps that follow should work fine.

1. Download and unpack apache maven from the link provided in the Glue Repo. This will create the `apache-maven-3.6.0` folder.
```sh
wget -qO- https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz | tar -xzvf -
```

2. Download and extract Apache Spark based on the glue version you will test, here we are testing glue 4.0. This will create the `spark` folder.

```sh
wget -qO- https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-4.0/spark-3.3.0-amzn-1-bin-3.3.3-amzn-0.tgz | tar -xzvf -
```

3. Dowload the aws-glue-libs from github. You should switch to the corresponding 
branch depending on which version of glue you are testing, here we are going to
test the 4.0, thus we keep it on the master branch. This step will create the `aws-glue-libs` folder.
```sh
git clone https://github.com/awslabs/aws-glue-libs.git
```

4. Export MAVEN_HOME, PATH and SPARK_HOME, you will need a jvm in your environment
as well. I just installed the default jdk.

```sh
export MAVEN_HOME=/full/path/to/where/you/downloaded/apache-maven-3.6.0 
export PATH=$PATH:/full/path/to/where/you/downloaded/apache-maven-3.6.0/bin
export SPARK_HOME=/full/path/to/where/you/downloaded/spark
```

5. Run maven install on aws-glue-libs
```sh
cd aws-glue-libs
mvn install
```

After all these steps, you should be able to test the glue `gluesparksubmit` executable, just `./bin/gluesparksubmit --help` on the aws-glue-libs folder.

## Now to the code please!

Well, after the configuration there is nothing much left to do. 
The `gluesparksubmit` executable will get a script and send it to run on executors
that are instantiated on the local machine. The executable will also manage the
executor context and other spark concepts, but wont allow much configuration unforntunatelly.

A important step here is how to use local files. Glue examples usually take s3 paths to fetch and process
data, but for a local example it made no sense to me. To make it run with local files
I had to use spark directly as you can check on the [./etl_demo.py](./etl_demo.py).

To run the code, after the configuration, just `./bin/gluesparksubmit /path/to/etl_demo.py`.