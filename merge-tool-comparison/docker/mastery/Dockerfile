FROM eclipse-temurin:11-jdk AS builder
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch master https://github.com/thufv/mastery.git /build/mastery
WORKDIR /build/mastery
RUN chmod +x gradlew && ./gradlew build -x test

FROM eclipse-temurin:11-jre
COPY --from=builder /build/mastery/build/libs/mastery-1.0-SNAPSHOT.jar /opt/mastery.jar
WORKDIR /workspace
ENTRYPOINT ["java", "-jar", "/opt/mastery.jar"]
