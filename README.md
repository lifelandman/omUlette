# omUlete
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
### I'm trying to export just an armature and it's animations, by using the setting to only export selected objects. however, I get an error.
omUlete is built in a way that can only generated animated objects in an egg file by first iterating through non-armature objects, and saving those that have a armature deformation for later.
I'd love to fix this so an armature without geometry could be exported, but that would require that the whole plugin be more or less rewritten from scratch.

### Why are some exported meshes randomly inside-out?
I swear this is blender's fault. Normaly blender stores loops in a counterclockwise order, which is what we need and expect. however, sometimes it just... doesn't. Ultimately fixing this would involve way more time and bloat. For now, try (scaling by -1 if your mesh is symetrical and) applying all scale transformations before recalculating the normals.
You can also/try instead recalculating the normals in the opposite direction. However, note that this is just a hacky way to swap the vertex order. Lighting will be the opposite of what it's supposed to be! \**gulp*\*
If all fails, don't forget that you're dealing with egg files and that you can manually edit the exported product. However, this means you'll have to make the edit on every export, so be careful.

### I'm exporting an animated charcter with the "Collapse Character Nodes" not ticked, but the final animation looks distorted!
This is because a panda3d character (That's the name of the class responsible for animation behind the actor class) expects that the origin of all geometry distorted by a skeleton to be the same as that of the skeleton itself.
(note: the origin of a skeleton in an egg file is really just the offset of all the top-level bones).

I considered making it so that the origin of deformed mesh is auto-adjusted to match that of any armature deforming it, but I realized that it's important for some modelers to know specifically where that origin is, so I didn't add that feature.

In fact, all you have to do to ensure that animation is in-fact getting exported correctly is to find the top of the animated character in the exported egg file and change _\<Dart> {Structured}_ to _\<Dart> {1}_ and the animation should look entirely as intended!
