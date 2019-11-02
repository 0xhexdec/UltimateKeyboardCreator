# UltimateKeyboardCreator - *Currently in Alpha*

The **UKC** is an open source skript for creating your own fully customized mechanical keyboard within Autodesk's [Fusion360](https://www.autodesk.com/products/fusion-360/overview#banner) (PC/Mac - [free for every hobbyist](https://www.autodesk.com/campaigns/fusion-360-for-hobbyists))

It is specially designed to generate 3D printable files but not restricted to only 3D printing.

The Keyboard is based on hand wired mechanical switches and a microcontroller (Teensy 2.0, Arduino Pro Micro, etc.), thus providing a custom, relatively cheap USB 2.0 compatible keyboard.

The UKC is designed to be extandable by users. The creation of new Frames can either be done by dropping in python modules that the UKC is handling automatically, or by dropping in parametric Fusion 360 Models, see [Drop-In Content](#drop-in-content).

## [Features](#features)

The UKC is build around the Cherry MX type switches and provides an easy to use creation of predefined keyboards that are as modifyable as possible without any knowlege in CAD. The UKC is also able to create only the layout plate to allow the free modeling of the surrounding frame. The free modeling of a fully custom Keyboard is **NOT** part of the UKC and will never be.

### What you can do with UKC

* Create a keyboard with predefined frame and predefined layout *(easy)*
* Create a keyboard with predefined frame and custom layout *(advanced)*
* Create a keyboard with custom frame and predefined layout *(based on your CAD skills)*
* Create a keyboard with custom frame and custom layout *(based on your CAD skills)*

### What you *can't* do with UKC

* Create a fully custom frame without *you* beeing able to use CAD
* Create a Keyboard with other switches than cherry MX style
* Create a PCB for the Keyboard

### Planned Features

* Creating custom keycaps

## [How to run it](#how-to-run-it)

Even the sourcecode is here, there is no need to clone the source if you just want to *use* the UKC (and not modify it).
Simply install the skript via the [Fusion360 Marketplace](#install-via-marketplace) to your Fusion360 and use it right away. **NOTE:** *there is currently no version available in the Fusio360 Marketplace, follow [install with source](#install-with-source) instead.*

### [Install via Marketplace](#install-via-marketplace)

[UKC on Fusion360 Marketplace](about:blank) - coming with first featurecomplete release

To run the skript either

* hit `Shift+S`
* click on **UltimateKeyboardCreator**
* hit `run`

or

* In the top menu, change from `SOLID` to `TOOLS`
* click on `Skripts and Add-Ins`
* click on **UltimateKeyboardCreator**
* hit `run`

### [Install with source](#install-with-source)

As Fusion360 supports Scripts and Add-Ins as simple drop-ins, you only have to download the source and put the extracted `UltimateKeyboardCreator` folder in your `Skripts` folder.

default location for `Skrips` folder on Windows: `%appdata%\Autodesk\Autodesk Fusion 360\API\Scripts`

or on Mac: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/Scripts`

Then, start up your Fusion360.

To run the skript either (weirdly, this is not possible right after startup)

* hit `Shift+S`
* click on **UltimateKeyboardCreator**
* hit `run`

or

* In the top menu, change from `SOLID` to `TOOLS`
* click on `Skripts and Add-Ins`
* click on **UltimateKeyboardCreator**
* hit `run`

## [How to use it](#how-to-use-it)

### [Creating a preset based Keyboard](#creating-a-preset-based-keyboard)

The UKC comes with a variety of different Keyboard Layouts. If you are looking for a easy to create Keyboard with a [well-known layout](#build-in-layouts), chances are high, the layout is already available. *(Otherwise create your own with the [Keyboard Layout Editor](http://www.keyboard-layout-editor.com) but be aware of the [current limitations](#known-limitations))*

### [Creating a custom Keyboard](#creating-a-custom-keyboard)

If you are willing to costumize your keyboard from the ground up, you can deactivate some features and design your Keyboard frame around the ready-to-use layout plate.

## [Build-In Layouts](#build-in-layouts)

* ANSI
  * 104 Keys (100%)
  * 104 Keys BIGASS (100%)
  * 87 Keys (80%)
  * 61 Keys (60%)
* ISO
  * 105 Keys (100%)
  * 88 Keys (80%)
  * 62 Keys (60%)
* JIS
  * currently none, coming soon
* OTHER
  * Keycool 82 (75%)
  * TADA68 (65%)
  * WhiteFox Aria (65%)
  * WhiteFox ISO (65%)

## [Build-In Frames](#build-in-frames)

Currently, in this early stage of development, only a very simple frame is available (in theory, I have to implement that still ¯\\\_(ツ)\_/¯ )

* UKC Default

## [Drop-In Content](#drop-in-content)

The UKC allows for two kinds of Drop-In content:

* [Python modules using the Fusion360 API](#python-modules)
* [Parametric Fusion360 Models with special requirements](#parametric-models)

### [Adding Custom Frames](#adding-custom-frames)

Adding custom frames to the UKC is easier than you maybe think. Ok... maybe adding custom frames via the API isn't that easy, but if you have some CAD skills, you can design a frame and make everybody happy. I try to make the basic workflow as easy as possible so everybody can contribute.

#### [Parametric Models](#parametric-models)

First things first: You need to know how to create a parametric model! That is the key point. At the importing stage (your model gets imported by the UKC to the current Component and gets merged with the layout plate), your model-parameters gets updated with values from the UKC (layout plate dimensions). Terefore you have to use these parameters in your design so it gets updated accordingly.

Your Design needs the following user-parameters:

`LayoutWidth` (Unit - mm)

the width of the Keyboard Layout Plate

`LayoutHeight` (Unit - mm)

 the height of the Keyboard Layout Plate

`InfillVoids` (Unit - No Unit)

if this is set to 0, the layout plate will get generated as normal, if it's set to 1, the free spaces between keys gets filled up to `VoidHeight`

`VoidHeight` (Unit - mm)

the height for the void-filling body

#### [Python Modules](#python-modules)

To create your own frame, you have to implement the `AbstractFrame` base class and put the module in the `modules\Frames` folder. The UKC will find your module and makes it available in the frame browser. To see what to do, check out the `UKC_Default.py` and the `AbstractFrame.py`.

Because all frame modules are loaded dynamically on request, the naming of the module and the class is important. You have two options for naming module and class:

1. the module (eg. `MyCustomFrame.py`) and class (eg. `MyCustomFrame`) names are the same,
2. the module name ends with an underscore (`MyCustomFrame_.py`) and the class name is `Frame`.

As spaces are not allowed in class and module names, thus making frame-names with spaces impossible, all underscores ("_") will be replaced by spaces in the frames browser.

## [Known Limitations](#known-limitations)

* not parsable data from the Keyboard-Layout-Editor (Maybe breaks the script)
  * Angled Keys
  * Any entry in *Custom Styles*
  * Any text (as in the Default *numpad* example)
  * images
* automatic lengthwise cutting of the keyboard is not supported (yet?)

## [Further useless Informations](#further_useless_informations)

Please, beloved reader and user, if you don't like the code style, found inefficiencies or just wonder how that piece of formatted junk is working anyway, keep in mind that this project is done in my spare time and my first python project till now. Normally, I am more used to hard-typed languages (like C, C++, Kotlin, Java, you name it) at hardware level so this plugin is, besides its obvious function, the project of *writing a plug-in* on its own.

The Idea for this script came a while ago, precisely: the idea for *a* script came a while ago, when I started to use Fusion 360 for modeling a Hydrofoil for Kitesurfing. I had some problems with designing the mast (wich required a airfoil profile) so I asked a friend (who knows a lot of CAD) to help me with this. He used the `ImportSlineCSV` Skript to get the profile in (at that moment, I was like: WHAT? That easy?) but had some problems with the scale (the script uses Fusion's default unit, "cm"). Because the used CSV was in millimeters, I thought: "Hey man, how hard could it be to change that, I am decent at programming, In can do that." (no, there is no "But it was way harder and I coded for an entire month"-moment, sorry, I took literally a minute) But I was a little hooked. I wanted to do more, even though I had to use Python, that untyped, whitespace-sensitive, bracket-free thing of language (I know I could use C++ but that whole compiling-debugging thing with some Fusion crashes left me with the conclusion, python is better for this task). It took over a year to get a good idea for a script that I want. I browsed Thingiverse and stumbled over the [SiCK-68](https://www.thingiverse.com/thing:3478494/files) keyboard by [Fedor Sosin](#special-thanks-to). I really liked the idea of a selfmade keyboard but I didn't liked the layout, that TADA68 isn't my style. I thought about making an "ISO 80%"-SiCK clone but realized, THAT'S my opportunity to create a script that creates a keyboard with different layouts. Started and daaayyum, that went nuts. Too many ideas and my vision to make it extendable and flexible made this project even more complex. But I don't regret anything. Even if nobody is ever reading this wall of text or is ever using this script. I liked and still like developing it. Maybe someone will create his or her own keyboard with this script and likes to type on that better than the keyboard before. That's the biggest honor I can get. By the way, I have written most of the code on my Laptop-Keyboard with a "sometimes-stuck"-W-key. Maybe I should build my own custom keyboard, maybe I should check for a script that allows me to create my own custom keyboard... maybe I should... **shut up and write the rest of the code**. But hey, have you noticed that your spacebar isn't working right? Maybe you should too...

## [Special Thanks to](#special-thanks-to)

Fedor Sosnin ([twitter](https://twitter.com/FedorSosnin)/[thingiverse](https://www.thingiverse.com/FedorSosnin/about)) and his awesome [SiCK-68](https://www.thingiverse.com/thing:3478494/files), [SiCK-PAD](https://www.thingiverse.com/thing:3682168) and [SiCK-60](https://www.thingiverse.com/thing:3671408) wich gave me the idea for this script.

Robert Sheldon *aka rsheldiii* ([thingiverse](https://www.thingiverse.com/rsheldiii/about)) for his **!awesome!** fully parametric [KeyV2 Library](https://www.thingiverse.com/thing:2783650). Thanks man, that helped me a lot!

Xiao Jin *aka fumbucker* ([thingiverse](https://www.thingiverse.com/fumbucker/about)) for her [Clueboard 660](https://www.thingiverse.com/thing:2897260) and providing the Fusion360 files.

D-Evolve ([thingiverse](https://www.thingiverse.com/csm67/about)) for his [custom keycaps](https://www.thingiverse.com/thing:2907297) and providing his Fusion360 files.

Kael Ruland ([twitter](https://twitter.com/kaelruland)/[thingiverse](https://www.thingiverse.com/kaelruland/about)) for his [SA](https://www.thingiverse.com/thing:2178185) and [DSA](https://www.thingiverse.com/thing:2172302) keycap sets and providing his STEP files.
