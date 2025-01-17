# base Image
FROM python:3.9.20-slim
# Install ssl upgrade because of vulnerability
# Update package list, upgrade OpenSSL, and clean up
RUN apt-get update && \
    apt-get install -y openssl && \
    apt-get upgrade -y openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Selenium and the Chrome WebDriver
# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libnss3 \
    libx11-xcb1 \
    libgconf-2-4 \
    libxi6 \
    fonts-liberation \
    libappindicator3-1 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Update package list and install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable=131.0.6778.204-1

    # Create a working directory
WORKDIR /app
# Copy the remaining files and source code
COPY . . 
# Install python packages
RUN pip install -r requirements.txt

# Expose port 5000 for FastAPI inside the container
EXPOSE 5000
# Start and run the Fast API app in the container
CMD ["python", "main.py"]