# Space Haven Modloader

This is an unofficial modding tool for [Space Haven by Bug Byte](http://bugbyte.fi/spacehaven/), an early-alpha spaceship colony sim.

It is **not associated with BugByte or Space Haven in any way** other than that it makes some modding possible for the game. This tool is intended as a sneak peek at what modding might be able to do, and in the future it will be replaced by BugByte's official mod support.


## Getting Started

Download the latest release from [the releases page](#) and fire it up.

![Screenshot](/screenshot.png?raw=true)

1. Make sure it found where you installed Space Haven. If it didn't, you'll need to locate it manually via the "Browse..." button in the top right corner.

2. Click the "Open Folder..." button to open your game's `mods` folder.

3. Download some mods and copy them in. There are a few example mods available from [the releases page](#) or you can find them elsewhere on the internet. When you're done your game folder should look something like this:

```
spacehaven.jar
savegames/
mods/
  artificial-plant/
    info
    library/
  exterior-air-vent/
    info
    library/
  ...
```

4. Go back to the mod loader and make sure the mods you installed appear in the list. If they don't then you might not have installed them properly. Double check the folder structure.

5. When you're ready click "Launch Spacehaven!" to play with mods. The mod loader will load the mods into the game, launch the game, and then unload them again when you quit.


## Modding Guide

Mods are stored as a series of XML files in the same format as the game's library.

You can take a look at the library by clicking the "Extract & annotate game assets" button. That will extract the game library from `spacehaven.jar` into `mods/spacehaven/` so you can take a look.

The main file of interest is `library/haven.annotated`, which is an annotated copy of `library/haven`, which is the main game library. It contains definitions for most of the things in the game (buildings, items, ships, characters, objectives, generation parameters, etc). Also of interest are `library/texts`, `library/animations`, and `library/textures`.

Mods follow the same folder structure and file format and should be reasonably obvious from the included sample mods.

Note that because mods are loaded by doing an id-wise merge with the base game library, only the following files and tags are currently supported:
- `Element`s in `library/haven`
- `AllAnimations/animations` in `library/animations`
- `t`s in `library/texts`


### ID Numbers

Most of the items in the game's library are identified by a numeric ID rather than a human-readable name.

If you want to replace an *existing* game definition, like the included Greenhouse mod does, simply copy that definition into to your mod with the same ID number that the game uses. The mod loader will replace the game's definition with the one from your mod.

If you want to create a *new* definition, things get a bit trickier because you need to make sure your ID numbers are unique across all mods that might get loaded. Luckily IDs can be any (positive) 32-bit integer which means there's lots of space.

I recommend prefixing your definition IDs with your Discord user number (e.g. mine is #4511) and a sequential mod number (e.g. I used `00` for the `artificial-plant` example, `01` for `exterior-air-vent`, etc) to come up with something reasonably unique, e.g. `45110200` for the Monster Meat crop recipe in the `greenhouse` example.


### Navigating the Library

ID numbers are reasonably easy to follow in a text editor - if you find a definition that references another, simply search for the referenced ID that you're interested in.

To find human-readable names, look for a `tid="###"` attribute and search for that ID in `library/texts`. Or, conversely, find the text in `library/texts` and search for the corresponding ID in `library/haven`.

For example, suppose we want to find the "Life Support" building. Starting from `/library/texts` and searching for "Life Support" we find:

```
    <lifeSupportName id="140" pid="139">
        <EN>Life Support</EN>
    </lifeSupportName>
```

We can then search for `tid="140"` in `library/haven` to find its definition:
```
    <me mid="927" ...>
        ...
        <objectInfo ...>
            ...
            <name tid="140" />
            <desc tid="141" />
            <subCat id="1508" />
            ...
        </objectInfo>
    </me>
```

Here we can see that the life support unit's ID is `mid="927"` and its build (sub-)category is `<subCat id="1508" />`. Searching for that ID we can find:

```
        <cat disabled="false" id="1508" order="3">
            <mainCat id="1505" />
            <button instance="536_BuildCatButtons1_subCat" />
            <name tid="869" />
        </cat>
```

and looking up the `<name tid="869" />` we see the category is named:

```
    <lifesupport id="869" pid="874">
        <EN>LIFE SUPPORT</EN>
    </lifesupport>
```

To make life easier, the mod loader does these name lookups automatically in a few places and stores the results in `_name=""` attributes on various tags. This annotated version of the library is saved to `library/haven.annotated` and is (accordingly) a bit easier to navigate.


### Textures and Animations

Extracting and annotating game assets also decodes and explodes the game's textures into `library/textures.exploded`. The game's original packed textures are written to `library/textures.exploded/*.png` and the texture regions are written to `library/textures.exploded/*/r*.png`, where the folder name is the texture sheet ID and the filename is the region ID.

Regions definitions can be found in `library/textures` in `<re n="..." />` tags and are used in `library/animations` by the `<assetPos a="..." />` tags.
