const fs = require("fs");
const path = require("path");
const mqtt = require("mqtt");

// Add the environment variables to your system or terminal
// Run with `node --env-file=.env mqtt.js` or only `node mqtt.js`

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

function onConnect() {
  console.log("Connected to MQTT broker");
  client.publish(
    `device/${DEVICE_ID}/request`,
    JSON.stringify({
      system: {
        sequence_id: 0,
        command: "ledctrl",
        led_node: "chamber_light",
        led_mode: "on",
      },
    }),
  );
}

function onMessage(topic, payload) {
  console.log(topic, payload.toString());
}

const HOSTNAME = process.env.DEVICE_HOSTNAME;
const DEVICE_ID = process.env.DEVICE_ID;
const ACCESS_CODE = process.env.DEVICE_ACCESS_CODE;

// const USERNAME = process.env.USERNAME;
// const ACCESS_TOKEN = process.env.ACCESS_TOKEN;

const client = connectLocalMQTT(HOSTNAME, DEVICE_ID, ACCESS_CODE);
// const client = connectCloudMQTT(USERNAME, ACCESS_TOKEN);

client.subscribe(`device/${DEVICE_ID}/report`);
client.on("connect", onConnect);
client.on("message", onMessage);
