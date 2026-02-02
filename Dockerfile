FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for cv2 and pdf tools
RUN apt-get update && apt-get install -y \
    build-essential \
        libgl1 \
            libglib2.0-0 \
                libxcb1 \
                    libxrender1 \
                        libxext6 \
                            libsm6 \
                                libfontconfig1 \
                                    && rm -rf /var/lib/apt/lists/*

                                    COPY requirements.txt .
                                    RUN pip install --no-cache-dir -r requirements.txt

                                    COPY . .

                                    ENV PORT=8000
                                    EXPOSE $PORT

                                    CMD ["python", "app.py"]
                                    
