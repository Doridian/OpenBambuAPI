# Cloud-relayed video

The on-printer video servers described in [`video.md`](./video.md) only
help while the consumer is on the same LAN as the printer. For
off-LAN access Bambu's network plugin opens one of several cloud-relay
transports and surfaces them behind a single `bambu:///…` URL string.
A client that wants to consume the video without using the proprietary
network plugin needs to recognise the URL form and implement the
matching transport.

## URL scheme dispatch table

The plugin's `Bambu_Create` / `Bambu_Open` entry point in
`libBambuSource.so` selects the transport from the URL prefix.
Observed prefixes (verified by triggering each path under
captured slicer sessions):

| Prefix | Transport | Notes |
|---|---|---|
| `bambu:///tutk?uid=<UID>&authkey=<KEY>&passwd=<PW>&region=<R>` | ThroughTek Kalay (TUTK) P2P | The `UID`/`authkey` come from the `POST /v1/iot-service/api/user/ttcode` cloud endpoint already documented in [`cloud-http.md`](./cloud-http.md). The plugin then drives the standard TUTK / IOTC AVAPI sequence (`IOTC_Initialize2` → `IOTC_Connect_ByUIDEx` → `avClientStartEx` → `avSendIOCtrl(IOTYPE_USER_IPCAM_START)` → `avRecvFrameData2`). |
| `bambu:///agora?app=<APP>&...` | Agora.io P2P | Used for the "go-live" / collaborative-print path. The query parameters carry app id, channel, and a per-session token. |
| `bambu:///local/<host>?...` | LAN port-6000 BambuTunnel | Direct TCP/6000 to the printer's IP; same transport described in [`video.md`](./video.md) for A1/P1 series. |
| `bambu:///rtsps___<rtsps-url>` | LAN RTSPS via live555 | The `<rtsps-url>` is a normal RTSPS URL with `://` replaced by `___` so the bambu:/// host shape is preserved. Used for X1 and P2S — points at port 322 on the printer. |
| `bambu:///rtsp___<rtsp-url>` | LAN RTSP (no TLS) via live555 | Same `___` substitution as the `rtsps___` variant; observed on a couple of dev/test builds. |

Same URL string round-trips through the plugin's
`bambu_network_get_camera_url` callback API, so a custom client
re-implementing that callback only needs to return one of these forms
to drive the matching transport in `libBambuSource.so`. A client
re-implementing the consumer side (i.e. replacing `libBambuSource.so`)
needs to be ready to dispatch on the same prefix list.

### URL fingerprint suffix

When `MediaPlayCtrl` in the slicer hands a `bambu:///…` URL off to
`Bambu_Create`, it appends a set of identifying query parameters:

```
&device=<dev_id>
&net_ver=<network plugin version>
&dev_ver=<printer firmware version>
&cli_id=<slicer's UUID, app_config slicer_uuid>
&cli_ver=<slicer version e.g. 02.07.00.55>
```

Independent clients that talk to `Bambu_Create` directly (rather than
via the slicer GUI) are observed to need to mirror these fields — the
plugin appears to fingerprint them, and `bambu:///tutk` opens have
failed in captures where the device or net_ver suffix was missing.
Verified on `bambu_network_agent/02.07.00.50`; other plugin builds may
relax this.

## H.264 codec-extradata format (BambuSource consumer side)

When a `libBambuSource.so` client calls the equivalent of
`Bambu_GetStreamInfo` on an open H.264 tunnel (the `tutk`, `agora`, or
`rtsps___` schemes above), the returned `StreamInfo.format_buffer`
field contains the codec extradata — the bytes a decoder needs to bring
up the parameter sets before it can decode any frame.

The observed layout in captures from H2S and H2D firmwares (other
models / firmwares not exhaustively re-checked):

- One SPS NAL unit (NAL type 7) followed immediately by one PPS NAL
  unit (NAL type 8).
- The two NALs are simply **concatenated**, with no length prefix and
  no start-code delimiter between them.
- Different captured streams have been seen to use either Annex-B
  framing (`0x00 0x00 0x00 0x01` start codes) or AVCC framing (each
  NAL prefixed with its 32-bit length in big-endian), and in some
  captures the buffer is bare NAL-unit bodies with no framing at all.

A defensive parser therefore needs to handle all three layouts. The
recipe that has been verified to feed the standard RFC-6184
`sprop-parameter-sets` field of an SDP and produce a decodable stream:

```c
// pseudocode
buf = format_buffer; sz = format_size;
while (sz > 0) {
    // try Annex-B start code (3 or 4 bytes)
    n = consume_annexb_start_code(buf, sz);
    if (n) { buf += n; sz -= n; }
    else {
        // try AVCC length prefix (u32 big-endian)
        len = read_u32_be(buf);
        if (len > 0 && len + 4 <= sz) {
            nal = buf + 4; nal_len = len;
            buf += 4 + len; sz -= 4 + len;
        } else {
            // fall through: treat whatever remains as one bare NAL
            nal = buf; nal_len = sz;
            buf += sz; sz = 0;
        }
    }
    nal_type = nal[0] & 0x1F;
    if      (nal_type == 7) sps = nal[0..nal_len];
    else if (nal_type == 8) pps = nal[0..nal_len];
}
```

Treating `format_buffer` as a single SPS NAL (i.e. assigning the entire
buffer to `sps` and leaving `pps` empty) decodes to a black screen
because the SDP `sprop-parameter-sets` ends up missing the PPS — that's
the failure mode that surfaced the parsing requirement.
