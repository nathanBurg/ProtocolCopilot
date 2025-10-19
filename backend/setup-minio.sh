#!/bin/bash

# Wait for MinIO to be ready
sleep 10

# Set up MinIO client
mc alias set myminio http://localhost:9000 minioadmin minioadmin

# Create protocols bucket if it doesn't exist
mc mb myminio/protocols --ignore-existing

# Set public read access for protocols bucket
mc anonymous set public myminio/protocols

echo "MinIO setup completed - protocols bucket is now publicly readable"
