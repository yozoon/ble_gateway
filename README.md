# BLE Gateway

## Installation
User install
```bash
python3 setup.py install --user
```

System install (required by the systemd service)
```bash
sudo python3 setup.py install
```

## Systemd Service

```bash
# Create a bluetooth user and add it to the existing bluetooth group (required for the systemd script)
sudo useradd -s /sbin/nologin -g bluetooth bluetooth

# Create the config directory
sudo mkdir /etc/ble_gateway/
sudo cp config.yaml /etc/ble_gateway/config.yaml

# Systemd service
sudo cp ble_gateway.service /etc/systemd/system/ble_gateway.service
sudo systemctl daemon-reload
sudo systemctl enable ble_gateway
sudo systemctl start ble_gateway
```