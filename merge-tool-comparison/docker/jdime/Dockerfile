FROM eclipse-temurin:17-jdk AS builder
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/se-sic/jdime.git /build/jdime
WORKDIR /build/jdime
RUN ./gradlew installDist

FROM eclipse-temurin:17-jre
COPY --from=builder /build/jdime/build/install/JDime /opt/jdime
RUN echo "text/x-java java" >> /etc/mime.types
WORKDIR /workspace
ENTRYPOINT ["/opt/jdime/bin/JDime"]
