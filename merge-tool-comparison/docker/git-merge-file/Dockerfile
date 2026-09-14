FROM alpine:3.19
RUN apk add --no-cache git
WORKDIR /workspace
ENTRYPOINT ["git", "merge-file", "--stdout"]
