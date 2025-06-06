# Basics

This file describes both GCode macros Bambu uses as well as custom GCode found.

# Headers

At least some of comment lines at the beginning of the file are necessary for functioning of the print. There are three major blocks with start and end guards:

- `HEADER_BLOCK_START`/`HEADER_BLOCK_END`
- `CONFIG_BLOCK_START`/`CONFIG_BLOCK_END`
- `EXECUTABLE_BLOCK_START`/`EXECUTABLE_BLOCK_END`

Excerpt:

```
; CONFIG_BLOCK_START
; accel_to_decel_enable = 1
; accel_to_decel_factor = 50%
```

Without some or most of these, the printer will hang with "Unzip" shown on the screen. 

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

## G28

- `G28 Z P0 T300; home z with low precision,permit 300deg temperature`

## G29

Bambu does not follow Marlin's G29 manual.

- `G29.2 S0 ; turn off ABL`
- `G29.2 S1` - Probably enables recording of height when probe detects collision and also could load saved calibration
- `G29 A1 X-1.4281 Y82.682 I67.984 J98.7461` - Probably does bed probing, guarded by g29_before_print_flag

## G39.4

Fires a canned command to detect build plate. Usually flag-guarded and followed by `M400`. It's likely important that Automatic Build Leveling is turned off first (with `G29.2 S0`).

## G380

Some have claimed it's a variant of `G38`, which is called "Probe Target". One use is in the section where the nozzle rubs itself on build plate overhang during cleaning, with code like:

```
G0 X90 Y-4 F30000
G380 S3 Z-5 F1200
G1 Z2 F1200
G1 X91 F10000
G380 S3 Z-5 F1200
G1 Z2 F1200
...
```

`Z` is the axis being zeroed and its movement direction, `F` is feedrate. `S` is custom to Bambu and unknown. There are two known values, `S2` and `S3`. `S2` is only used in this one section:

```
;=====avoid end stop =================
G91
G380 S2 Z30 F1200
G380 S3 Z-20 F1200
G1 Z5 F1200
G90
```

The above section is used early and the head moves up, down, and back up slightly, just as it appears.

## G392

- `G392 S0` - Appears to *toggle* "clog detect"? Because it's commented as both enabling and disabling clog detect at different times.
  Done just after initial bed heating and before the "avoid end stop" then "reset machine status" sections.

## M73.2

- `M73.2   R1.0 ;Reset left time magnitude`

## M106

- `M106 P1 S0-255` - set part cooling fan speed (0 off, 255 100%)
- `M106 P2 S0-255` - set aux fan speed
- `M106 P3 S0-255` - set chamber fan speed

## M109

Causes screen to update to say "Heating", in addition to the usual wait for heating.

## M400

M400 is "Finish Moves". Marlin doesn't document any arguments. Bambu uses these:

- `M400 S#` - sleep for about # seconds
- `M400 P300` - probably sleep 300 milliseconds; S & P probably can be used together

## M620

- `M620 C#` - calibrate AMS by AMS index
- `M620 R#` - refresh AMS by tray index
- `M620 P#` - select AMS tray by tray index
- `M620 M` - Commented ";enable remap"; only done once before the first M620 command.
- `M620 S#` - Starts a branch; if "Enable AMS" is NOT checked, then gcode is skipped until the matching `M621 S#` is found. Commented "select AMS by tray index", but that likely refers to the whole block of commands and not this single command.
  - Seems to only be used for unloading filament during machine_end_gcode since at least 20221103.
  - `#` = 255 when unloading filament at end of print for non-H2D. It's just a constant that was in AMS code from the beginning.
  - `#` = 65535 and 65279 are used during H2D unload. They are simply hardcoded in the machine end code. (65279 is 0x100 less than 65535)
- `M620 S#A` - Starts a branch; if "Enable AMS" is NOT checked, then gcode is skipped until the matching `M621 S#A` is found.
  - Not sure what the `A` does differently. Used for filament change during print, and not for the final unload during machine end sequence.
  - Does being in this branch as an effect on `T` commands? The `T1000` falls outside a `M620` branch, but `T255` is within the matching one.
  - Does this branch if the intended filament is already loaded?
  - What happens if external filament is loaded?

## M620.1

- `M620.1 E F[old_filament_e_feedrate] T{nozzle_temperature_range_high[previous_extruder]}` - Seems to set extrusion parameters that will be used by `T` during load/unload.
  - Used before and after `T` during filament changes and shortly after `T` during initial load.
- `M620.1 X# Y# F# P<0/1/2>` - Prefaced with comment "; get travel path for change filament" when used with X1 and AMS? See [comment](https://github.com/bambulab/BambuStudio/issues/1661#issuecomment-1522800180).

## M620.3

- `M620.3 W1; === turn on filament tangle detection===`

## M620.10

- `M620.10 A0 F[old_filament_e_feedrate]` - It's used just prior to a `T` opcode during filament changes, but not during initial load or unload. Introduced with long retraction.
- M620.10 A1 F[new_filament_e_feedrate] L[flush_length] H[nozzle_diameter] T[nozzle_temperature_range_high] - Used shortly after `T` during filament change. 

## M620.11

Introduced with "long retraction when cut".

- `M620.11 S1 I[previous_extruder] E-{retraction_distances_when_cut[previous_extruder]} F1200` - Run before tool change if the current filament has long retraction enabled.
- `M620.11 S1 I[previous_extruder] E{retraction_distances_when_cut[previous_extruder]} F{old_filament_e_feedrate}` - Run after tool change if the old filament had retraction enabled.
- `M620.11 S0` run when the filament-being-unloaded does not have a long retraction before and after tool change (`T`).
- `M620.11 S1 I# E# F#` - Does not cause any action to occur
  - `I` always matches the number of the `M620 S#` block, but unknown whether this is enforced.

## M621

- `M621 S#` - End of branch from `M620 S#`
- `M621 S#A` - End of branch from `M620 S#A`

## M622

Flags are judged by `M1002`.

- `M622 J1` If last judged flag was true, then continue; otherwise skip commands until `M623` is found.
- `M622 J0` If last judged flag was false, then continue; otherwise skip commands until `M623` is found.

## M622.1

- `M622.1 S0` - Always run just before dynamic extrusion M9833
- `M622.1 S1 ; for prev firware, default turned on` - seems this turns on whatever this is that is usually already on.

## M623

- `M623` end of branch from `M622`

## M630

- `M630 S0 P0` - used early in "reset machine status", unknown purpose

## M960

- `M960 S5 P0/1`- turn off (0) or on (1) the logo light on toolhead
- `M960 S4 P0/1`- turn off (0) or on (1) the nozzle light 

## M971

Take photo (for timelapse).

## M973

- `M973 S1` - likely enable scanner
- `M973 S2 P16000` - likely perform scan
- `M973 S3 P1` - camera start stream
- `M973 S4` - disable scanner

## M975

- `M975 S1` - turn on vibration supression
  - Run many times so something could be resetting it

## M976

- `M976 S1 P1` - first layer scan
- `M976 S2 P1` - hot bed scan before print

## M981

- `M981 S0 P20000` - disable spaghetti detector
- `M981 S1 P20000` - enable spaghetti detector

## M982.2

- `M982.2 S1 ; turn on cog noise reduction`

## M991

- `M991 S0 P{layer_num}` - commented "notify layer change"
- `M991 S0 P-1` - commented "end timelapse at safe pos" but that doesn't seem right.


## M1002

- `M1002 gcode_claim_action : 0` - Display message on screen, 0 is probably clear message. [More numbers on forum.bambulab](https://forum.bambulab.com/t/bambu-lab-x1-specific-g-code/666). Notably:
  - 1 is auto bed leveling
  - 2 is heatbed preheating
  - 4 is changing filament
  - 5 is M400 U1 pause
  - [Full(?) list at bambulab forum](https://forum.bambulab.com/t/bambu-lab-x1-specific-g-code/666)
- `M1002 set_filament_type:TYPE` - Probably updates display? TYPE can be `UNKNOWN` or `PETG`, `PLA`, `TPU-AMS`, `TPU`, etc.
- `M1002 judge_flag FLAGNAME` - Used by `M622` to branch. Some FLAGNAMEs:
  - `build_plate_detect_flag` - whether you have build plate detection enabled
  - `g29_before_print_flag` - G29 is automatic bed leveling
  - `extrude_cali_flag` if "Flow Dynamics Calibration" is enabled when starting print
  - `filament_need_cali_flag` - ??
  - `timelapse_record_flag` - If timelapse is enabled when starting print
  - `g39_3rd_layer_detect_flag`

## M1003

- `M1003 S0` - disable power loss recovery
- `M1003 S1` - enable power loss recovery

## M1006

Allows playing music with the stepper coils. If the printer is configured not to play the tone, it doesn't do anything, presumably. Example line:

- `M1006 A44 B20 L100 C39 D20 M100 E48 F20 N100`

## M1007

- `M1007 S0` - unknown purpose.
  - Done as second command following clog detect disable, during i.e. filament change
- `M1007 S1` - done before printing following filament change and during after initialization shortly before printing starts.

## M9833.2

- `M9833.2` - follows turning off clog detect in the beginning; unknown purpose.

## T

Tool change.

- `T255` (also `T65535` in H2D I think) - Only used during tool change when AMS is unloaded when the print is over. At least causes it to cut and have AMS retract filament.
- `T1000` - Used twice in the following sequence during startup only AFAICT:

  ```
  M975 S1 ; turn on vibration compensation
  G90     ; Absolute positioning
  M83     ; override G90 and put the E axis into relative mode independent of the other axes
  T1000   ; ???
  ```

  What does it do if there is a filament already loaded? What does it do if it doesn't?

- `T#` - Many canned actions to orchestrate movements of AMS motor and extruder. Cuts filament, goes to purge location, has AMS retract current filament, uses both AMS and extruder motors in a delicate dance mediated by sensors (will try 3 times to load filament, for example, then error). The number is zero-indexed, but references the one-indexed list of filaments displayed in the GUI and also written in `slice_info.config` in the 3MF.
  - If a bare `M17` hasn't been run since steppers were last messed with, this command will freeze.
  - Seems to freeze if not set up perfectly; the printer will allow you to press stop and cancel print, but then the print is never cancelled. Requires power cycle. Unsure how many of the setup commands are required.
