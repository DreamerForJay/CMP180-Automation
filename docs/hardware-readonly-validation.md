# CMP180 first hardware validation

Status: ready after offline tests pass
Scope: connection verification only; no RF output and no WLAN measurement writes

## When the instrument is needed

Do not connect the CMP180 while implementing configuration, Mock workflows,
unit tests, or GUI layout. Connect it only after the complete offline suite is
green and the working tree is clean.

## Preconditions

1. CMP180 is reachable at `192.168.200.50`.
2. The PC and CMP180 remain on the existing `192.168.200.0/24` lab network.
3. CMsquares is not in the middle of a measurement or configuration change.
4. `configs/instrument.example.yaml` uses:

   ```yaml
   address: "TCPIP::192.168.200.50::5025::SOCKET"
   options: "SelectVisa='socketio'"
   clear_status_on_connect: false
   reset_on_connect: false
   ```

5. `configs/scpi_command_map.yaml` still has every CMP180-specific generator,
   WLAN TX, and result command set to `null`.

## Allowed first-pass traffic

Only the following queries are allowed:

- `*IDN?`
- `*OPT?`
- `SYST:ERR?`

The first pass must not send `*RST`, `*CLS`, generator configuration, WLAN
configuration, measurement initiation, routing changes, or RF ON/OFF commands.

## Command

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm test-connection `
  --instrument-config configs\instrument.example.yaml
```

## Acceptance criteria

- Command exits with code `0`.
- ID contains `Rohde&Schwarz` and `CMP`/`CMP180`.
- Options response is captured without parsing failure.
- Error queue terminates with `0,"No error"` or equivalent.
- CMsquares workspace, routing, generator state, and RF state are unchanged.

After this passes, CMP180-specific SCPI discovery remains a separate manual,
reviewed step. A successful connection test does not authorize RF ON or an EVM
measurement.
