# Basics

This file describes both GCode macros Bambu uses as well as custom GCode found

# Macros

## AMS unload

```gcode
M620 S255
M104 S250
G28 X
G91
G1 Z3.0 F1200
G90
G1 X70 F12000
G1 Y245
G1 Y265 F3000
M109 S250
G1 X120 F12000
G1 X20 Y50 F12000
G1 Y-3
T255
M104 S25
G1 X165 F5000
G1 Y245
G91
G1 Z-3.0 F1200
G90
M621 S255
```

## AMS load

```gcode
M620 S[next_tray_index]
M104 S250
G28 X
G91
G1 Z3.0 F1200
G90
G1 X70 F12000
G1 Y245
G1 Y265 F3000
M109 S250
G1 X120 F12000
G1 X20 Y50 F12000
G1 Y-3
T[next_tray_index]
G1 X54  F12000
G1 Y265
M400
M106 P1 S0
G92 E0
G1 E40 F200
M400
M109 S[new_filament_temp]
M400
M106 P1 S255
G92 E0
G1 E5 F300
M400
M106 P1 S0
G1 X70  F9000
G1 X76 F15000
G1 X65 F15000
G1 X76 F15000
G1 X65 F15000
G1 X70 F6000
G1 X100 F5000
G1 X70 F15000
G1 X100 F5000
G1 X70 F15000
G1 X165 F5000
G1 Y245
G91
G1 Z-3.0 F1200
G90
M621 S[next_tray_index]
```

## Manual axis move X, Y or Z

```gcode
M211 S
M211 X1 Y1 Z1
M1002 push_ref_mode
G91
G1 X# F#
M1002 pop_ref_mode
M211 R
```

## Manual E move

```gcode
M83
G0 E# F#
```

## Model scan for first layer

```
M976 S1 P1
M400 P100
```

# Custom commands

## M106

- `M106 P1 S0-255`- set part cooling fan speed (0 off, 255 100%)
- `M106 P2 S0-255`- set aux fan speed
- `M106 P3 S0-255`- set chamber fan speed

## M620

- `M620 C#` - calibrate AMS by AMS index
- `M620 R#` - refresh AMS by tray index
- `M620 P#` - select AMS tray by tray index
- `M620 S#` - select AMS by tray index

## M621

- `M621 S#`- load filament in AMS by tray index

## M960

- `M960 S5 P0/1`- turn off (0) or on (1) the logo light on toolhead
- `M960 S4 P0/1`- turn off (0) or on (1) the nozzle light 

## M973

- `M973 S1` - likely enable scanner
- `M973 S2 P16000` - likely perform scan
- `M973 S3 P1` - camera start stream
- `M973 S4` - disable scanner

## M976

- `M976 S1 P1` - first layer scan
- `M976 S2 P1` - hot bed scan before print

## M981

- `M981 S0 P20000` - disable spaghetti detector
- `M981 S1 P20000` - enable spaghetti detector

## M1003

- `M1003 S0` - disable power loss recovery
- `M1003 S1` - enable power loss recovery
