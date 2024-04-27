# Stage 1: Build stage
FROM ubuntu:20.04 AS builder

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    openjdk-8-jdk \
    wget

# Set up environment variables
ENV ANDROID_SDK_ROOT /home/user/Android/sdk
ENV FLUTTER_HOME /home/user/flutter
ENV PATH $PATH:$ANDROID_SDK_ROOT/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$FLUTTER_HOME/bin

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user

# Clone the Flutter app repository
RUN git clone https://github.com/karemSD/Mimal-Shop-app.git && \
    cd Mimal-Shop-app && \
    flutter pub get

# Stage 2: Production stage
FROM builder AS production

# Run the Flutter app
CMD ["flutter", "run"]
