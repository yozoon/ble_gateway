```bash
# Create a bluetooth user (required for the systemd script)
sudo useradd -s /sbin/nologin -g bluetooth bluetooth

# Create the config directory
sudo mkdir /etc/ble_mqtt_gateway/
sudo cp config.yaml /etc/ble_mqtt_gateway/config.yaml

# Systemd service
sudo cp ble_mqtt_gateway.service /etc/systemd/system/ble_mqtt_gateway.service
sudo systemctl daemon-reload
sudo systemctl enable ble_mqtt_gateway
sudo systemctl start ble_mqtt_gateway
```