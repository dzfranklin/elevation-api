FROM --platform=arm64 rust:bookworm as builder

WORKDIR /build

RUN apt-get update && apt-get install -y pkg-config libclang-dev libgdal-dev

COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {println!(\"Hello, world!\");}" > src/main.rs
RUN cargo build --release

COPY src src
RUN cargo build --release

FROM --platform=arm64 debian:bookworm-slim

RUN apt-get update && apt-get install -y libssl-dev libgdal-dev ca-certificates

COPY --from=builder /build/target/release/elevation-api /

ENTRYPOINT ["/elevation-api"]
