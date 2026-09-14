FROM eclipse-temurin:17-jre
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget -q -O /opt/spork.jar \
    https://github.com/ASSERT-KTH/spork/releases/download/v0.5.0/spork-0.5.0.jar
WORKDIR /workspace
ENTRYPOINT ["java", "-jar", "/opt/spork.jar"]
