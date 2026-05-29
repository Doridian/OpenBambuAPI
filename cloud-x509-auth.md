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

## Envelope Construction

The notes below cover the exact construction used to build a `header`
envelope that the firmware accepts, so an independent client can
produce byte-identical envelopes. The shape was deterministic across
multiple captured envelopes from different slicer sessions.

### Header field semantics

| Field | Value type | Derivation |
|---|---|---|
| `sign_ver` | string | `"v1.0"` (only value observed) |
| `sign_alg` | string | `"RSA_SHA256"` (RSA PKCS#1 v1.5 padding, SHA-256 digest) |
| `cert_id` | string | leaf certificate's `tbsCertificate.serialNumber` as a lowercase 32-char hex string, optionally suffixed with `CN=<leaf-host>` (see "Certificate ID Format" above) |
| `payload_len` | integer | byte length of the canonical bytes-to-sign described below |
| `sign_string` | string | base64 of the RSA-SHA256 signature over the canonical bytes-to-sign |

### Canonical bytes-to-sign

The signing input is reconstructed from the top-level command class
(only `print` has been observed to require signing, per the auth
requirements table further down) and a canonicalised JSON
serialisation of the inner object:

```
bytes_to_sign = '{"<top-key>":' + canonical_json(envelope[<top-key>]) + '}'
```

where `canonical_json()` is JSON serialised with:

- keys sorted alphabetically (recursively, at every depth)
- no whitespace anywhere
- `,` and `:` as the only separators

In Python this matches:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"))
```

`payload_len` is then the byte length of the resulting `bytes_to_sign`
string (UTF-8 / ASCII, since the canonical form contains no
non-ASCII bytes for any observed envelope).

### Verification recipe

The construction can be verified end-to-end against a captured envelope
and the corresponding leaf certificate (selected via the `cert_id`
prefix):

```python
import base64, json
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509 import load_pem_x509_certificate

env = json.load(open("envelope.json"))
cert = load_pem_x509_certificate(open("leaf.pem", "rb").read())
pubkey = cert.public_key()

canonical_inner = json.dumps(env["print"], sort_keys=True,
                             separators=(",", ":"))
to_sign = b'{"print":' + canonical_inner.encode() + b"}"

assert len(to_sign) == env["header"]["payload_len"]
sig = base64.b64decode(env["header"]["sign_string"])
pubkey.verify(sig, to_sign, PKCS1v15(), SHA256())
print("Signature verified.")
```

Corrections welcome if the canonicalisation differs for other
command classes or firmware tracks not yet captured.

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

## Inner `param_enc` transform (gcode_line only)

For `print.command = "gcode_line"` payloads, the network plugin appears to
apply an additional transform **before** the outer envelope above is
built and signed: the plaintext `param` field is removed and replaced
with `param_enc`, whose value is the original gcode string RSA-encrypted
with the **printer's** RSA public key (distinct from the per-slicer
client certificate's keypair used for the outer signature). The
resulting JSON is then run through the canonical-bytes-to-sign
computation and signed as usual.

Schematically:

```jsonc
// what an application produces
{
  "print": {
    "command": "gcode_line",
    "param": "M1002 set_gcode_claim_speed_level: 5\n",
    "sequence_id": "1234"
  }
}

// what is actually published to MQTT
{
  "print": {
    "command": "gcode_line",
    "param_enc": "<base64 of RSA-encrypted bytes of the param string>",
    "sequence_id": "1234"
  },
  "header": { /* sign_string covers the param_enc form */ }
}
```

Properties observed in captures (P1S / H2S firmwares; not exhaustively
re-checked against every printer model):

- The same plaintext `param` yields a different `param_enc` value each
  publish — consistent with PKCS#1 v1.5 padding (random padding bytes).
- The transform applies only to `gcode_line`. Other `print.*` payloads
  (`gcode_file`, `pause`, `resume`, `stop`, `print_speed`, …) keep
  their fields verbatim and rely on the outer signature alone.
- The encryption key is the printer's RSA pubkey, not the slicer's
  client certificate keypair. The slicer obtains it through a
  `cert_report` reply that the printer publishes after the MQTT
  subscription is established (the same round-trip
  `install_device_cert` triggers).

A native re-implementation of the signing path therefore needs to:

1. Subscribe to the printer's MQTT report topic and capture the
   `cert_report` reply, then parse out the printer's RSA pubkey.
2. For `gcode_line` only, RSA-encrypt the `param` value with that
   pubkey, base64-encode it, and place it under `param_enc`.
3. Run the canonical-bytes-to-sign computation in §"Signing Details" on
   the resulting JSON (with `param_enc`, not `param`).

Without this inner transform, the firmware appears to respond with
`result:"failed"` on the `/report` topic and the gcode line is
silently dropped.

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
