#!/bin/sh
# Build the password file from environment variables at start-up (no secret in the repo).
set -eu
mkdir -p /mosquitto/run
PW=/mosquitto/run/passwd
: > "$PW"
add() { [ -n "$2" ] || { echo "missing password for $1" >&2; exit 1; }; mosquitto_passwd -b "$PW" "$1" "$2"; }
add edge-vsite01 "$MQTT_PASS_EDGE_VSITE01"
add edge-ev01    "$MQTT_PASS_EDGE_EV01"
add ingest       "$MQTT_PASS_INGEST"
add dispatcher   "$MQTT_PASS_DISPATCHER"
add health       "$MQTT_PASS_HEALTH"
chown -R mosquitto:mosquitto /mosquitto/run /mosquitto/data
chmod 0700 "$PW"
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
