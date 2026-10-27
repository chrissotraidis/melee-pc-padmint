# Melee PC for PadMint

Build a personal iPhone/iPad copy of **999sian/melee-pc 0.4.2 with the save-creation fix** on your own Mac. This is a separate app from MeleePad.

This repository and its releases contain the recipe, small source patches and build scripts only. PadMint downloads the pinned upstream source and compiles it locally. Your game disc, saves, signing information and finished app stay on your computer. No prebuilt game app is offered here.

## Build with PadMint

You need an **Apple Silicon Mac (M1 or newer)**, full **Xcode with its iOS platform**, **Rustup**, an internet connection and **15 GB of free space**. Windows, Intel Mac, Linux and phone-only builds are not available for this recipe.

1. Install Xcode, open it once to finish setup, and select its command-line tools in **Xcode → Settings → Locations**. Install the **iOS** platform in **Settings → Components** if missing.
2. [Install Rustup](https://rustup.rs/) if it is not already installed. PadMint shows the setup command and a **Check again** button. The recipe installs the pinned Rust 1.96.0 iPhone compiler automatically.
3. Download **PadMint 0.5.19 or newer** from [PadMint releases](https://github.com/chrissotraidis/padmint/releases/latest), unzip it, and open **PadMint.command** in the new folder. An older PadMint folder has an older game list.
4. Select **Melee PC**, choose **iPhone/iPad**, and follow the setup/build steps. CMake, Ninja and the pinned GNU ARM64 compiler are downloaded automatically. The game file is selected in the app afterward.
5. Keep the resulting personal `.ipa` private. Install it with your own signing tool, or import it into your existing LiveContainer setup. **For this test, use a new app/data container and keep your existing container and saves intact.** LiveContainer compatibility still needs the reporter's confirmation.
6. Transfer your own **USA revision 2 (NTSC-U 1.02)** Melee disc image to Files on the phone. In the app, tap **Choose Disc** and select it. ISO, CISO and RVZ are supported by this recipe. Game assets are not included in the IPA.

The recipe version is **0.1.0**; the personal app identifies itself as **Melee 0.4.2, build 54**. Do not use the in-app upstream updater for this test: upstream updates do not necessarily include this patch.

## Check saving

In a fresh test container, choose **Yes** when asked to create Game Data. Confirm that creation finishes and the game continues. Then change **Options → Sound → music/sound balance**, back out to the main menu to let it save, close the game completely, and reopen it. The changed balance should still be there.

Use the balance slider for this check: the port's Stereo/Mono option is a temporary system setting and resets separately from the memory-card save. Keep [MeleePad #53](https://github.com/chrissotraidis/meleepad/issues/53) open until the reporter confirms creation, saving and reloading in their setup. Report the app build, device, iOS and LiveContainer versions, and which step failed; do not upload your disc, save, IPA or identity.key.

## What was tested

The same save/resource patches passed new-save creation and a changed game preference surviving a cold restart on a physical iPhone 14 running iOS 27.0.1. This was native iOS, not LiveContainer. A clean PadMint player check with Apple's Python 3.9.6 and an empty PadMint folder also produced a valid personal IPA with iOS scene startup. Neither establishes broad gameplay, audio or performance acceptance.

## Source and build details

- Upstream: [999sian/melee-pc](https://github.com/999sian/melee-pc), pinned to `0fb0af3304d3469308b5574369a6ec86f145632f`, based on doldecomp/melee and Aurora.
- The save patch routes title/date formatting through a fixed-argument native helper, avoiding the generic AArch64 versus Apple variadic calling-convention mismatch at that call.
- The resource patch changes the bundle directory name to `game-resources`, which allows Apple's signing tools to accept the flat iOS app bundle.
- GNU ARM64 GCC 15.2.0 is downloaded with a verified SHA-256. Rust is pinned to 1.96.0. Xcode supplies the Apple compiler and SDK. The wrapper adapts compiler flags and assembly data directives; it retains the upstream game ABI.
- `PersonalBuild.json` records source/recipe revisions, patch hashes, compiler input and executable identity in each personal app. No Apple credentials or provisioning profile are copied by the recipe.

The app compiles decompiled game code from upstream source; it reads assets from the player's disc at runtime. It does not translate game code from that disc. Read [upstream licensing](https://github.com/999sian/melee-pc/blob/0fb0af3304d3469308b5574369a6ec86f145632f/licenses/LICENSE.md) for the distinction between the unlicensed game code, GPL port code and third-party components. This repository preserves upstream attribution. Its recipe code is GPL-3.0-or-later; see [COPYING](COPYING).

For maintainer validation from current PadMint main:

```sh
scripts/player-check.sh melee-pc ios - /absolute/path/to/clean/recipe-checkout
# After publishing, verify the public route:
scripts/player-check.sh melee-pc ios -
```

Public recipe assets must pass both PadMint's audit and the private release gate. The generated IPA remains personal-only; its content findings are recorded by PadMint and do not make it a public release. No gate is disabled.
