# Client Plugin Internals

> Notes on a few compile-time constants observed inside the network plugin
> that ships with BambuStudio (the slicer's network agent process).
>
> These are baked into the plugin binary and appear to be identical for
> every installation — they are not derived from anything user-specific
> and anyone can re-extract them from their own slicer install. They are
> only useful for inspecting your own slicer's behaviour (e.g. decrypting
> your own network log files for debugging).

## Debug log encryption

The network plugin writes its internal log stream to files of the form:

```
~/.config/BambuStudio/log/debug_network_<timestamp>.log.enc
```

(equivalent paths on macOS / Windows under the per-user BambuStudio data
directory)

These files are an spdlog stream encrypted with **AES-128-ECB** using a
16-byte ASCII key embedded in the plugin:

```
yyuBcftO2jkZeucy
```

A one-liner to decrypt your own log file:

```sh
openssl enc -d -aes-128-ecb -nopad \
  -K "$(printf yyuBcftO2jkZeucy | xxd -p)" \
  -in ~/.config/BambuStudio/log/debug_network_*.log.enc | strings
```

The decrypted stream contains spdlog binary format-ID prefixes interleaved
with the formatted message text, so piping through `strings` (or a small
spdlog-aware parser) gives the most readable output. Each record begins
with a timestamp like `[2025-…] [I] [T <tid>]:` followed by the message.

This is handy for debugging your own slicer's MQTT / HTTPS behaviour
without having to attach a debugger.

## Analytics upload encryption

The plugin periodically uploads `*_track_*.zip.enc` and `*_cache_*.zip.enc`
bundles for analytics / crash reporting. The encryption is **AES-256-CBC**
and three baked-in ASCII constants are visible adjacent to the relevant
code:

```
IXdE2DUTsO7b6k58rwZn1b0bWHZysj8d   (32 bytes)
p6nTAFdtBS4G4PiE                   (16 bytes)
hCUSRUX6huMKP7I9                   (16 bytes)
```

The 32-byte string is the AES-256 key; the two 16-byte strings appear to
be IVs for the two upload categories (`_track_` vs `_cache_`), but the
exact pairing is best confirmed against a captured bundle.

These are noted here mostly for completeness — if you care about what your
slicer is sending home, you can decrypt the bundles you find on disk
before they're uploaded.

## Plugin self-version string

The plugin reports its own version internally as e.g.:

```
bambu_network_agent/02.07.00.50
```

This version is **independent** of the slicer it ships alongside — for
example a slicer build labelled `02.07.00.55` may carry a plugin whose
internal version is `02.07.00.50`. If you're correlating bug reports or
log files across installs, the agent version string is what matters for
the network layer, not the slicer's user-facing version.

## Studio binary verification (the "signed studio" gate)

Before the plugin will **sign** outbound `print.*` control commands, it
verifies that its host process is a genuine, Bambu-signed BambuStudio
install. This gate is what makes *control* commands require a signed
client even though *status/reads* flow regardless: an unsigned control
publish is silently dropped by post-2025 firmware, which the slicer sees
as `BAMBU_NETWORK_SIGNED_ERROR` (`-26`) — see
[cloud-x509-auth.md](cloud-x509-auth.md) for the signing/cert flow itself.

Observed on Windows, plugin `02.07.00.x`. The plugin Authenticode-verifies
**two** modules with `WinVerifyTrust`:

1. the host executable — resolved via `GetModuleFileName(NULL)`
   (`bambu-studio.exe`)
2. `BambuStudio.dll` — the slicer's network-agent code that `LoadLibrary`s
   the plugin (resolved via `GetModuleFileName(hDllBase)`)

For each module it extracts the signer certificate and compares the
publisher to a pinned identity:

| Field | Value |
|-------|-------|
| Subject | `Shanghai Lunkuo Technology Co., Ltd` (older builds pinned `Shenzhen Tuozhu Technology Co., Ltd.`, that cert expired 2026-02-10) |
| Issuer | `GlobalSign GCC R45 EV CodeSigning CA 2020` |

The comparison is on the certificate's **full identity (public key / SPKI)**,
not just the subject string — a self-signed certificate that merely copies
the subject, serial and issuer name does *not* pass. If either module is
unsigned or from another publisher, the plugin logs
`process_network_msg, unsigned_studio` (and `add sign info failed`); the
command then ships unsigned and the printer rejects it.

The open-source slicer does an *additional*, independent same-publisher
check before it will even load the plugin: `SummarizeSelf()` /
`IsSamePublisher()` (in `src/slic3r/Utils/CertificateVerify.cpp` /
`NetworkAgent.cpp`) compare the host's signer SPKI to the plugin DLL's. A
host signed by a different publisher than the plugin is refused with
`module is from another publisher`, and the slicer falls into its
plugin-redownload loop.

### Note for custom / forked builds (interoperability)

A locally-built (unsigned) BambuStudio fork therefore can read status from
your own printers but cannot get its *control* commands signed. Because the
gate checks the genuine signed binaries — not anything secret — you can
interoperate using the official binaries you already have installed,
without any private key:

- Launch with a **genuine, version-matched** official `bambu-studio.exe`.
  It is a thin launcher that `LoadLibrary`s `BambuStudio.dll` and calls the
  exported `bambustu_main(int argc, char** argv)`; a fork's DLL exports the
  same entry, so the genuine launcher will happily run your DLL. This
  satisfies check #1. **Version match matters** — e.g. a `02.06` launcher
  against a `02.07` plugin faults inside the (now-activated) signing path;
  align the exe, `BambuStudio.dll` and plugin to the same `02.07.00.x`.
- Satisfy check #2 by pointing the plugin's verification of your
  `BambuStudio.dll` at the genuine official `BambuStudio.dll` — e.g. an
  in-process inline hook on `GetModuleFileNameW/A` (and `CryptQueryObject`)
  installed *before* the plugin loads, returning the official DLL's path
  when the plugin resolves your fork's DLL.

With both module checks satisfied the plugin self-decrypts its embedded app
key and signs `print.*` normally, so commands are accepted by the printer.

---

Corrections and additions welcome — these are observations from a single
slicer build, and behaviour may differ across platforms or versions.
