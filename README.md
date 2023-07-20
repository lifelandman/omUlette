# ZABEE-tenative-name-
A quick and easy, lightly-featured panda3d egg exporter blender plugin.

![image](https://user-images.githubusercontent.com/77763745/230818181-f3439022-67fb-4f12-aab9-eee694c8433d.png)



## Instalation
This plugin has no dependencies. Just install the zip-file included with the release like any other blender addon.
If you want to compile from source, just put ZABEE-main inside of a zip-file.

## Usage
Once you have enabled the addon, just select "egg (panda3d)" from file-export.
Before exporting, be sure to adjust the imageDir variable. this should be the directory your textures will be in relative to the model directory as specified in your config file.
All geometry will be exported. In the future, I might make it so this is more intellegent.

Multitexturing is not yet supported. The only texture applied to exported geometry is the first one specified per node-based material.

## Notes
At the time of writing, this exporter is in a very early state. It only supports textures and static geometry, although this is eventually planed to change.
