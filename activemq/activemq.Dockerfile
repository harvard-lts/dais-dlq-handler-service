FROM openjdk:8-jdk-alpine

ENV ACTIVEMQ_VERSION=5.16.3
ENV ACTIVEMQ_DOWNLOAD_URL=https://archive.apache.org/dist/activemq/${ACTIVEMQ_VERSION}/apache-activemq-${ACTIVEMQ_VERSION}-bin.tar.gz
ENV ACTIVEMQ_DIRECTORY=/opt/apache-activemq

RUN wget ${ACTIVEMQ_DOWNLOAD_URL} \
    && tar -xzf apache-activemq-${ACTIVEMQ_VERSION}-bin.tar.gz && rm apache-activemq-${ACTIVEMQ_VERSION}-bin.tar.gz

RUN mv apache-activemq-${ACTIVEMQ_VERSION} ${ACTIVEMQ_DIRECTORY}
RUN sed -i "s|127.0.0.1|0.0.0.0|g" ${ACTIVEMQ_DIRECTORY}/conf/jetty.xml
# Copy ActiveMQ config file with DLQ policy
COPY ./activemq/activemq.xml ${ACTIVEMQ_DIRECTORY}/conf/activemq.xml

WORKDIR ${ACTIVEMQ_DIRECTORY}/bin

ENTRYPOINT ["./activemq","console"]
