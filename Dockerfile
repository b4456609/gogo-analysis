FROM ubuntu:14.04


# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl wget build-essential gcc

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

RUN apt-get install -y  software-properties-common
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get -y update

RUN echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
RUN sudo apt-get install -y oracle-java8-installer

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

RUN apt-get -y install curl
RUN curl -s http://apache.stu.edu.tw/spark/spark-1.6.1/spark-1.6.1-bin-hadoop2.6.tgz | tar -xz -C /opt/

# Set the default directory where CMD will execute
WORKDIR /opt/app

# Copy the application folder inside the container
ADD DataAnalyzer.py /opt/app
ADD WeatherClient.py /opt/app
ADD WeatherServiceClient.py /opt/app
ADD requirements.txt /opt/app

# Get pip to download and install requirements:
RUN pip install -r requirements.txt

EXPOSE 4040
ENTRYPOINT ["/opt/spark-1.6.1-bin-hadoop2.6/bin/spark-submit"]
CMD ["DataAnalyzer.py"]
