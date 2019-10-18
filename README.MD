# UltimateKeyboardCreator - *Currently in Alpha*

The **UKC** is an open source skript for creating your own fully customized mechanical keyboard within Autodesk's [Fusion360](https://www.autodesk.com/campaigns/fusion-360-for-hobbyists) (PC/Mac - free for every hobbyist)

It is specially designed to generate 3D printable files but not restricted to only 3D printing.

## [How to run it](#how-to-run-it)

Even the sourcecode is here, there is no need to clone the source if you just want to *use* the **UKC** (and not modify it).
Simply install the skript via the [Fusion360 Marketplace](#install-via-marketplace) to your Fusion360 and use it right away.

### [Install via Marketplace](#install-via-marketplace)

[UKC on Fusion360 Marketplace](about:blank) - coming soon

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

## [How to use it](#how-to-use-it)

### [Creating a preset based Keyboard](#creating-a-preset-based-keyboard)

The **UKC** comes with a variety of different Keyboard Layouts. If you are looking for a easy to create Keyboard with a [well-known layout](#build-in-layouts), chances are high, the layout is already available. Otherwise create your own with the [Keyboard Layout Editor](http://www.keyboard-layout-editor.com) but be aware of the [current limitations](#known-limitations)

### [Creating a custom Keyboard](#creating-a-custom-keyboard)

If you are willing to costumize your keyboard from the ground up, you can deactivate some features and design your Kayboard frame around the ready-to-use layout plate.

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
  * more coming soon

## [Known Limitations](#known-limitations)

* not parsable data from the Keyboard-Layout-Editor (Maybe breaks the script)
  * Angled Keys
  * Any entry in *Keyboard Properties* (Metadata object)
  * Any entry in *Custom Styles*
  * Any text (as in the Default *numpad* example)
  * images
