#!/bin/bash

# Create monitoring network
docker network create monitoring

# Start Prometheus
docker run -d \
  --name prometheus \
  --network monitoring \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Start Grafana
docker run -d \
  --name grafana \
  --network monitoring \
  -p 3000:3000 \
  -v $(pwd)/grafana-dashboard.json:/etc/grafana/provisioning/dashboards/image-processing.json \
  grafana/grafana

# Start Prometheus Pushgateway
docker run -d \
  --name pushgateway \
  --network monitoring \
  -p 9091:9091 \
  prom/pushgateway

echo "Monitoring stack is now running:"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- Pushgateway: http://localhost:9091" 