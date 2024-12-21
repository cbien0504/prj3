# Use Airflow image as the base
FROM apache/airflow:2.8.3

# Install required packages
USER root

# Install wget and gnupg for downloading and verifying the packages
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    apt-get clean

# Download and install OpenJDK 8 from AdoptOpenJDK or other sources
RUN wget https://adoptopenjdk.net/archive.html?variant=openjdk8&jvmVariant=hotspot -P /tmp && \
    wget https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u362-b09/OpenJDK8U-jdk_x64_linux_hotspot_8u362b09.tar.gz -P /tmp && \
    tar -xvzf /tmp/OpenJDK8U-jdk_x64_linux_hotspot_8u362b09.tar.gz -C /opt && \
    rm /tmp/OpenJDK8U-jdk_x64_linux_hotspot_8u362b09.tar.gz && \
    mv /opt/jdk8u362-b09-jdk8 /opt/jdk

# Set JAVA_HOME and PATH
ENV JAVA_HOME=/opt/jdk
ENV PATH="$JAVA_HOME/bin:$PATH"

# Verify Java installation
RUN java -version

# Switch back to airflow user
USER airflow
