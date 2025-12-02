# homecad

[CadQuery](https://github.com/CadQuery/cadquery) scripts I wrote for 3D printing at my home.

I know very very little about CAD or CadQuery, or 3D printing. Those scripts are in poor code quality. Experts can probably implement them much more elegantly.

## Generate `.stl` files for slicing software used by 3D printers

Ensure [`cadquery`](https://pypi.org/project/cadquery/) is installed, then simply run the scripts:

    cd src
    python3 command_strip_plate.py  # or other scripts

`.stl` files will be written to `~/stl`. Some scripts might generate multiple `.stl` files as different parts or variants. The scripts can also be edited in [CQ-editor](https://github.com/CadQuery/CQ-editor) which provides a nice interactive preview.

## Examples

<!-- generated-examples -->
<table>
<thead>
<tr>
<th>
Description
</th>
<th>
Rendered Preview
</th>
</tr>
</thead>
<tbody>
<tr>
<td>
<details>
<summary>
Snap-on two-plate mounting system for Command Refill Strips
</summary>

**Plates to the left (thinner)**

The back plate (the thiner one) is meant to be attached to a wall using [3M Command Refill Strips](https://www.amazon.com/dp/B073XR4X72).

The front plate (the thicker one) can be attached to objects that need to be mounted.

The two plates snap together to hold the object in place. When removal is needed, the front plate can be detached easily, exposing the pull tab of the Command strip.

**Plates to the right (thicker)**

This is a variant to support rotation. It's useful to be embedded in a photo frame so it can rotate 90 degree. 2x5x10mm magnet holes are reserved to lock the designed rotation locations.

</details>

[154.3 x 5.7 x 70.0 mm](https://github.com/quark-zju/homecad/blob/master/src/command_strip_plate.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/command_strip_plate.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Corner connector for curtain tracks
</summary>

The stock connector of the [curtain track](https://www.amazon.com/dp/B0BB1PS5NW) has a smaller radius (7cm) that is not smooth enough for automation (SwitchBot). I need a larger one.

Requires drilling and M2.5 screws to fix the connector to the metal tracks.

</details>

[250.2 x 250.2 x 22.0 mm](https://github.com/quark-zju/homecad/blob/master/src/curtain_track_full.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/curtain_track_full.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Deadbolt sensor - Magnet holder
</summary>

Similar to [this "Invisible Zigbee Deadbolt Sensor" project](https://www.instructables.com/Invisible-Zigbee-Deadbolt-Sensor/).

I use [10x5x2mm magnets](https://www.amazon.com/dp/B0B6PBXBVJ). This is the holder for the magnets. It fixes the magnet to the 5x5mm lock cylinder.

</details>

[9.2 x 13.2 x 14.0 mm](https://github.com/quark-zju/homecad/blob/master/src/deadbolt_magnet_holder.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/deadbolt_magnet_holder.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Deadbolt sensor - Contact sensor holder
</summary>

Similar to [this "Invisible Zigbee Deadbolt Sensor" project](https://www.instructables.com/Invisible-Zigbee-Deadbolt-Sensor/).

I use [a smaller Zigbee contact sensor](https://www.amazon.com/dp/B0FPX7874R). This is the holder for the contact sensor. In my case, there is no need for wiring or soldering. I only need to remove the shell of the device.

</details>

[48.2 x 14.8 x 30.0 mm](https://github.com/quark-zju/homecad/blob/master/src/deadbolt_sensor_holder.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/deadbolt_sensor_holder.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Frame for e-ink display
</summary>

For [Waveshare's 13.3 inch E6 color display](https://www.waveshare.com/13.3inch-e-paper-hat-plus-e.htm).

There are a bunch of E6 color displays in the market in 2025. However, they either have a worse form factory (large padding area around the picture, smaller display), or use a restricted software stack.

I use a Raspberry Pi Zero 2W, with [PiSugar 3](https://www.amazon.com/dp/B0FB3N1YSK) for scheduled power-on. ESP32-WROVER can also be a decent choice.

The waveshare's example dithering algorithm might produce suboptimal color accuracy. I [updated the script](https://gist.github.com/quark-zju/e488eb206ba66925dc23692170ba49f9) to produce more accurate colors.

The frame size exceeds the build plate I use. Initially, I made a one-piece frame that can print vertically. It requires lots of support and took 7h to print, and the `|Z` lines turned non-straight.

The current version uses multiple parts that fit the build plate to print horizontally, and supports rotation.

</details>

[235.0 x 14.0 x 297.0 mm](https://github.com/quark-zju/homecad/blob/master/src/epd_frame.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/epd_frame.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Polish KW1 keys for print
</summary>

Polish KW1 models generated by [keygen](https://github.com/ervanalb/keygen) so they can be printed and actually used.

More specifically,
- Cut it thinner to avoid overhang and size mismatch.
- Deepen the slot to avoid mismatch.

To generate `a.stl` for a KW1 key:

```
keygen scad/kwikset.scad --bitting 12345
```

CadQuery cannot import `.stl`. So `.stl` needs to be converted to `.step` first. To convert `.stl` to `.step` using FreeCAD:
- Open the `.stl` file.
- Switch to "Part" workspace.
- Part -> Create shape from mesh.
- Part -> Convert to solid.
- File -> Export.

The example `k1a` and `k1b` use bitting 12345 and 76543.

</details>

[1.6 x 56.3 x 43.8 mm](https://github.com/quark-zju/homecad/blob/master/src/kw1_polish.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/kw1_polish.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Stand for pens
</summary>

This is a stand for the [Panda Wiggle Gel Pens](https://www.hitchcockpaper.com/products/panda-wiggle-gel-pen). It holds the bamboo upright for a more realistic look.

</details>

[64.8 x 39.4 x 20.0 mm](https://github.com/quark-zju/homecad/blob/master/src/pen_stand.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/pen_stand.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Holder for rack edges
</summary>

This is a holder that can attach to the edges of [racks like this](https://www.amazon.com/dp/B09W2Y51TC/).

It can be useful to stick something like a [Pico remote](https://www.amazon.com/Lutron-3-Button-Wireless-Lighting-PJ2-3BRL-WH-L01R/dp/B00KLAXFQ0) to the rack.

</details>

[26.8 x 36.5 x 10.0 mm](https://github.com/quark-zju/homecad/blob/master/src/rack_edge_holder.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/rack_edge_holder.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Switchbot curtain bot fixer
</summary>

Lock the locations of the [W-shaped curtain hooks](https://www.amazon.com/dp/B096ZXQ6PD) around the [Switchbot curtain bot (U-rail)](https://www.amazon.com/SwitchBot-Automatic-Curtain-Opener-High-Performance/dp/B0C6XZYFS7) so the bot less likely runs into the hook and gets stuck.

</details>

[60.0 x 130.0 x 6.0 mm](https://github.com/quark-zju/homecad/blob/master/src/switchbot_curtain_bot_hook_fix.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/switchbot_curtain_bot_hook_fix.svg" /></p>

</td>
</tr>
<tr>
<td>
<details>
<summary>
Thinkpad X13 (Gen 4) thin stand
</summary>

A small stand for the ThinkPad X13 (Gen 4) that sits under the cooling area to prevent uneven surfaces from blocking airflow.

Includes slots for [20 × 20 × 1 mm magnet tiles](https://www.amazon.com/dp/B0DBVHMRW5).

</details>

[140.0 x 96.1 x 3.0 mm](https://github.com/quark-zju/homecad/blob/master/src/thinkpad_x13_thin_stand.py)

</td>
<td>

<p align="center"><img src="https://github.com/quark-zju/homecad/raw/master/img/thinkpad_x13_thin_stand.svg" /></p>

</td>
</tr>
</tbody>
</table>

<!-- generated-examples -->
