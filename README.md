# OpenTTD for phone browsers

> **Disclaimer:** this project is intended for people who own a copy of
> Transport Tycoon Deluxe. If you don’t own the original game, please buy it before using this app.

[OpenTTD](https://www.openttd.org) (the free, open-source remake of Transport Tycoon Deluxe)
compiled to WebAssembly, with a page made for playing on a phone in landscape.

The ready-to-host site is in [`docs/`](docs/), as plain static files. Any static host will do
(GitHub Pages from `/docs`, Vercel, Netlify, Cloudflare Pages…). It needs HTTPS for the
offline mode and "Add to Home Screen".

## What's different from the stock web build

- **Touch controls**: tap = click, one-finger drag = scroll the map (or drag-build with a tool),
  two-finger drag = scroll even while a tool is selected, pinch = zoom,
  long-press = right-click (tooltips stay up while you hold).
- **Aim mode** (crosshair button): one finger moves the cursor like a trackpad and never clicks;
  a round CLICK button for the other thumb clicks (tap) or holds the button down (hold, for
  drag-building). Slide off the button before releasing to cancel. Options in the menu: tap on the
  map jumps the cursor there; CLICK button in the bottom-left or bottom-right corner.
- **Side button bar** in the notch area: zoom in/out, "next tap is a right-click",
  Esc (cancel tool; double-tap = close top window), on-screen keyboard, menu.
- **Works with rotation lock on**: when the phone reports portrait, the app turns itself 90° so you can
  just hold the phone sideways (menu → "Flip upside down" switches direction).
- **In-app keyboard** that turns with the game (the iPhone keyboard cannot). It opens by itself when
  a text box is being edited, and slides the game up so the box stays visible (`patches/0003`).
- **Trimmed game UI** (`patches/0002`): no zoom buttons in the toolbar (the page has its own) with the
  other buttons widened to fill the space, and no Exit button in the main menu, whose buttons are larger.
- **Solid black status bar** on iPhone, so the game never sits under the clock or Dynamic Island.
- **Always saved** (`patches/0004`): autosave every minute, an extra save the moment the app goes to the
  background, and a **Continue** button at the top of the main menu that loads the newest save.
- **Back (undo)** (`patches/0004`): up to 5 in-memory snapshots taken just before the player's own
  actions (failed actions don't count; actions within half a second are one step). Back reloads the
  latest one.
- **Phone-friendly first-run settings**: drag-to-scroll, right-click tooltips, monthly autosave, no survey popup.
- **Home-screen app**: web manifest + service worker, so it runs full-screen and offline once installed.
- **Save import/export** and **original TTD files**: import `.sav`/`.sv1` saves, or your own
  original TTD `TRG*.GRF` + `SAMPLE.CAT` files to play with the original graphics and sounds.
  (They stay on your device; this repo does not include any original game files.)
- Engine patches (`patches/`): right-button drag scrolls the map in every scroll mode (two-finger pan),
  plus the toolbar/main menu and text-box changes above.

Ships with the free [OpenGFX](https://github.com/OpenTTD/OpenGFX) graphics and
[OpenSFX](https://github.com/OpenTTD/OpenSFX) sounds. No music (the browser build has no MIDI player).

## Rebuilding

```sh
./build.sh                    # OpenTTD 15.3 by default; OPENTTD_VERSION=… to change
PORTS_VIA_GIT=1 ./build.sh    # if your network blocks GitHub archive downloads
```

Needs git, cmake, ninja, python3, curl, unzip and a C++ compiler. Emscripten 3.1.57 (the version
OpenTTD pins) is installed automatically. Output goes to `docs/`.

## Licence

OpenTTD is GPL v2: source at https://github.com/OpenTTD/OpenTTD (tag `15.3`), plus the patch
in `patches/`. OpenGFX and OpenSFX are GPL v2 / CC-BY-SA as stated in their packages.
