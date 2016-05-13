FROM ubuntu:14.04


RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-software-properties
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common

RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get -y update


RUN echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
RUN sudo apt-get install -y oracle-java8-installer

RUN apt-get -y install curl
RUN curl -s http://apache.stu.edu.tw/spark/spark-1.6.1/spark-1.6.1-bin-hadoop2.6.tgz | tar -xz -C /opt/

EXPOSE 8080 7077 8081
CMD ["/opt/spark-1.6.1-bin-hadoop2.6/sbin/start-master.sh"]