const fs = require("fs");
const path = require("path");
const mqtt = require("mqtt");

const bblCA = fs.readFileSync(path.join(__dirname, "ca_cert.pem"));

function connectLocalMQTT(hostname, deviceID, accessCode) {
  return mqtt.connect({
    protocol: "mqtts",
    hostname,
    port: 8883,
    connectTimeout: 4e3,
    clean: true,
    username: "bblp",
    password: accessCode,
    servername: deviceID,
    ca: bblCA,
  });
}

function connectCloudMQTT(username, accessToken) {
  return mqtt.connect({
    protocol: "mqtts",
    hostname: "us.mqtt.bambulab.com",
    port: 8883,
    connectTimeout: 4e3,
    clean: true,
    username,
    password: accessToken,
  });
}
