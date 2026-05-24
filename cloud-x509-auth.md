# X.509 Certificate Authentication

> Post-January 2025 firmware authentication flow  
> Captured from Bambu Handy app (v3.x) communicating with a P1S printer

## Background

In January 2025, Bambu Lab pushed firmware requiring X.509 certificate authentication for local MQTT commands. The app exchanges a token with the cloud API to obtain per-device certificates, then signs all MQTT command payloads.

See also: [Hackaday: X.509 Certificate and Private Key Extracted](https://hackaday.com/2025/01/19/bambu-connects-authentication-x-509-certificate-and-private-key-extracted/)

## Certificate Exchange Flow

### 1. Request Device Certificate

```
GET /v1/iot-service/api/user/applications/{appToken}/cert?aes256={encrypted}&ver=1
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `appToken` | path | Base64url-encoded application token (generated client-side) |
| `aes256` | query | AES-256 encrypted payload containing device identity |
| `ver` | query | Endpoint version selector; observed value is `1` |

The app token is a long base64url string (100+ chars). The AES payload is similarly encoded.

Recent slicer builds are observed to always include `&ver=1` as an
additional query parameter; the endpoint appears to require it.

**Example URL (tokens redacted):**
```
https://api.bambulab.com/v1/iot-service/api/user/applications/QqTHQ6X9gFy9...=/cert?aes256=ViXLbxLlpySi...&ver=1
```

**Response:** X.509 certificate and private key for the specific printer.

### 2. List Active Certificates

The app queries active certificates via MQTT:

```json
{
  "security": {
    "sequence_id": "2040",
    "command": "app_cert_list",
    "timestamp": 1772675132281,
    "type": "app"
  }
}
```

**Response (on MQTT report topic):**

```json
{
  "security": {
    "sequence_id": "2040",
    "command": "app_cert_list",
    "timestamp": 1772675132281,
    "type": "app",
    "cert_ids": [
      "9bed8c27b4bf69582d58f11abaaad99fCN=GLOF3813734089.bambulab.com",
      "77bcfb6303214f046175eb6681a46d83CN=GLOF3813734089.bambulab.com"
    ]
  }
}
```

Multiple certificates can be active simultaneously.

### 3. Sign MQTT Commands

All MQTT commands include a `header` object with the RSA signature:

```json
{
  "user_id": "3469901296",
  "print": {
    "ams_id": 0,
    "command": "extrusion_cali_sel",
    "filament_id": "GFL99",
    "nozzle_diameter": "0.4",
    "nozzle_volume_type": "normal",
    "sequence_id": "2039",
    "timestamp": 1772675132270,
    "tray_id": 3
  },
  "header": {
    "sign_ver": "v1.0",
    "sign_alg": "RSA_SHA256",
    "sign_string": "iq3gpC6U2UijAp+v+YDJduXkPIDO5UaUjq1k72Xw6Ps...",
    "cert_id": "77bcfb6303214f046175eb6681a46d83CN=GLOF3813734089.bambulab.com",
    "payload_len": 225
  }
}
```

## Certificate ID Format

The `cert_id` format is:

```
{hex_fingerprint}CN={serialNumber}.bambulab.com
```

Where:
- `hex_fingerprint` is a 32-char lowercase hex string. In captured envelopes
  captured this matched the leaf certificate's
  `tbsCertificate.serialNumber` rather than an MD5 over the cert. You can
  check against your own capture with:

  ```sh
  # leaf.pem = the cert the client presented for this session
  openssl x509 -in leaf.pem -serial -noout
  # → the hex value should match the cert_id prefix (before any CN= suffix)
  ```
- `serialNumber` is the printer's serial number (e.g., `GLOF3813734089`)

## Signing Details

| Field | Value |
|-------|-------|
| `sign_ver` | `v1.0` |
| `sign_alg` | `RSA_SHA256` |
| `sign_string` | Base64-encoded RSA-SHA256 signature of the payload |
| `cert_id` | Certificate identifier (see format above) |
| `payload_len` | Byte length of the signed payload |

The `sign_string` is computed by:
1. Serializing the command payload (everything except `header`) as JSON
2. Signing with RSA-SHA256 using the private key from the certificate exchange
3. Base64-encoding the signature

## Per-Printer Client Certificates

> The notes below are from observing a slicer talk to a single printer over LAN MQTT; some of this may be incomplete or wrong for other firmware tracks. Contributions / corrections are always welcome.

The cert returned by the `/cert` endpoint above is a per-printer client certificate. Observations about the certificate:
- The leaf has `CN=<printer serial>` and chains up to BBL CA (the same chain bundled in [`examples/ca_cert.pem`](./examples/ca_cert.pem)).
- It appears to be long-lived (the leaves I've looked at have ~10-year validity windows).
- The printer firmware appears to accept any client cert that chains to BBL CA and whose CN matches its own serial; I haven't found other constraints.

A given slicer install ends up holding one such cert+key per printer it has been bound to.

### Where it's used

The cert+key is presented during the TLS handshake to the printer's MQTT broker (`mqtts://<printer-ip>:8883`). It is *separate* from the `bblp` / LAN access code username+password, which is checked after the TLS handshake completes.

### Auth requirements per command class

For local MQTT, the cert+key on the TLS handshake is one layer; the `header`-signed envelope described above is a second layer that only some command classes require. Best guess from captured slicer traffic:

| Top-level JSON key | TLS client cert+key | Signed envelope (`header`) | Firmware response if envelope missing/bad |
|---|---|---|---|
| `pushing.*` / `info.*` | Required to subscribe to `/report`; publish accepted with cert+key alone | No | n/a |
| `system.*` / `camera.*` / `xcam.*` | Required (broker rejects the TLS handshake otherwise) | No | n/a |
| `print.*` (publish to `/request`) | Required | Required | `result:"failed"`, `reason:"mqtt message verify failed"`, `err_code:0x05024007` if no envelope; `0x05024009` if envelope is present but malformed |
| `print.*` (subscribe via `/report`) | Required | n/a | n/a |

The two `err_code` values above seem to be firmware-defined and are easy to misattribute to credential or topic-ACL problems, so they're probably worth knowing about when implementing a client.

### Obtaining the cert+key for testing

If you have your own slicer install bound to your own printer, the per-printer cert+key can be recovered without modifying the slicer or its plugin: after the slicer has connected to the printer at least once, the leaf cert and private key live in the network plugin process's heap in PEM form, and can be recovered by scanning anonymous-memory regions of `/proc/<pid>/mem` for `-----BEGIN CERTIFICATE-----` and `-----BEGIN PRIVATE KEY-----` markers (ptrace is sufficient; no plugin patching required). This is the currently known user-facing extraction method. If others are found, PRs welcome!

## Additional MQTT Commands Observed

### extrusion_cali_sel

Select filament for extrusion calibration (not in original OpenBambuAPI docs):

```json
{
  "print": {
    "ams_id": 0,
    "cali_idx": -1,
    "command": "extrusion_cali_sel",
    "filament_id": "GFL99",
    "nozzle_diameter": "0.4",
    "nozzle_volume_type": "normal",
    "sequence_id": "2039",
    "timestamp": 1772675132270,
    "tray_id": 3
  }
}
```

## TUTK (ThroughTek) P2P Protocol

The app uses ThroughTek Kalay for P2P camera streaming alongside MQTT:

```json
{
  "json": {
    "cmdtype": 256,
    "sequence": 2376,
    "notify": {
      "topic": "device/01P00C5A1002021/report",
      "size": 243
    }
  },
  "data_length": 243
}
```

TUTK connection codes are obtained via:

```
POST /v1/iot-service/api/user/ttcode
```

(Already documented in [cloud-http.md](cloud-http.md))

## Filament IDs

| ID | Material |
|-----|----------|
| `GFL99` | Bambu PLA Basic |
| `GFL98` | Bambu PLA Matte |
| `GFL00` | Bambu PLA Basic (Red) |
| `GFA00` | Bambu PLA Basic (Black) |
| `GFA05` | Bambu PLA Basic (White) |
| `GFB99` | Bambu PETG Basic |
| `GFN99` | Bambu PA6-CF |
| `GFS99` | Bambu Support W |
| `GFU99` | Bambu TPU 95A |
