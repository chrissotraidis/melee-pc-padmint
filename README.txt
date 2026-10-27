Melee PC personal build recipe for PadMint

This is a LOCAL, UNPUBLISHED candidate, separate from MeleePad. It wraps pinned
999sian/melee-pc 0.4.2 and the tested save-comment fix. No upstream game source,
keys, game images, personal IPA or signing material is shipped in this recipe.
PadMint downloads source/tools and builds the app on the player's own Mac.
The app reads game assets from the player's own USA revision 2 disc after install;
it compiles decompiled game code from upstream source, not from that disc.

Requirements: Apple Silicon Mac, full Xcode with iOS platform, Rustup, network
access, and at least 15 GB free. PadMint supplies CMake/Ninja. The recipe pins
Rust 1.96.0 and GNU ARM64 GCC 15.2.0 (download verified by SHA-256).
Windows, Intel Mac, Linux and phone-only builds are not implemented here.

Developer validation from current PadMint main:
  scripts/player-check.sh melee-pc ios - /absolute/path/to/this/clean/checkout

For a checked-out recipe, PadMint also supports:
  python3 -m padmint tools melee-pc --repo /path/to/recipe --target ios
  python3 -m padmint build melee-pc --repo /path/to/recipe --revision FULL_RECIPE_COMMIT --target ios
These are existing commands, but this candidate is not in the public PadMint
catalog. Normal player UI / padmint make availability requires a reviewed hosted
recipe release plus a separate catalog entry. Do not replace the existing
MeleePad catalog item: it builds a different app/runtime.

Output: unsigned personal IPA. Use the player's existing signing/install tool.
No Apple credentials, signing identity or device profile is requested or copied
by the recipe. Preserve the existing LiveContainer app/container; validate the
new app in a separate test container first. Import the player's own game file,
choose Yes to create a save, change a saved game preference, restart the app,
and verify the preference persists. Do not send the IPA or game files back.
Keep issue 53 open until the reporter confirms their result.

The locally tested development build passed create/save/reload on an iPhone 14,
iOS 27.0.1. LiveContainer was not tested. This candidate's own fresh PadMint
build status is recorded separately in the investigation's player-check log.
Public recipe inputs must pass both content gates. The personal IPA is expected
to be non-public: PadMint records its content findings without turning the output
into a distributable release. No gate is changed or bypassed.

Upstream attribution: https://github.com/999sian/melee-pc at
0fb0af3304d3469308b5574369a6ec86f145632f, based on doldecomp/melee and Aurora.
Read upstream licenses/LICENSE.md for its separation of game code, original
GPL-3.0-or-later port code and third-party licenses. The source patches preserve
upstream file names and change only save formatting and local bundle resources.
