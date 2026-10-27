# Melee PC for PadMint

Build a personal iPhone/iPad copy of **Melee PC 0.4.2 with maintained compatibility patches** on your own Mac or GitHub’s hosted Mac. This is a separate app from MeleePad.

This repository and its releases contain the recipe, small source patches and build scripts only. PadMint downloads the pinned upstream source and compiles it on the selected Mac. Your game disc, saves and signing information are not needed during compilation. Local builds stay on your computer; GitHub builds store the personal IPA in your private repository for one day. No prebuilt game app is offered here.

## Build on GitHub without a Mac

This route uses the same maintained recipe as the local build. [A real GitHub-hosted build passed](https://github.com/chrissotraidis/padmint/actions/runs/40473291597/job/122085358107) on 27 October 2026 with Xcode 26.3, finishing in about 6½ minutes. You only need a browser and a GitHub account; GitHub supplies the Mac, Xcode and build tools.

Use a **private repository**, because anyone with read access to a public repository can download its Actions artifacts. A public fork cannot be made private, so use a separate imported copy. The workflow refuses this game's artifact-producing run in a public repository. GitHub's private-repository Actions allowance applies; check your usage/budget first. If the allowance is exhausted, GitHub may block the run or bill according to your account settings. See [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

1. Sign in to GitHub and open [Import repository](https://github.com/new/import). Enter `https://github.com/chrissotraidis/padmint.git` as the source URL, choose your account as owner, name the new repository `padmint-personal`, select **Private**, and choose **Begin import**. Wait for the import to finish. No credentials are needed for the public source repository. [GitHub's import guide](https://docs.github.com/en/migrations/importing-source-code/using-github-importer/importing-a-repository-with-github-importer) explains this screen.
2. In your new private repository, open **Actions** and enable workflows if prompted. If Actions is disabled, open **Settings → Actions → General** and allow actions for this repository. On a phone, use the workflow sidebar/menu to reveal the list.
3. Choose **Build a game for iPhone and iPad → Run workflow**, keep branch **main**, select **melee-pc**, and press the green **Run workflow**. You do not need to install PadMint or Xcode on your computer. Do not upload your disc, saves, Apple ID or signing certificate.
4. Open the run and wait for the green success check. While signed in, download **melee-pc-iphone-…** under **Artifacts**, then unzip it to get the `.ipa` and `SHA256SUMS`. Download within **one day**. On iPhone, open the ZIP in Files to extract it.
5. In your existing LiveContainer, tap **+** and select the extracted IPA. Use the new **Melee PC** app with a fresh data container, keeping the old app/container intact. Alternatively, install the IPA using your normal signing tool.
6. Open Melee PC, tap **Choose Disc**, select your own USA revision 2 / NTSC-U 1.02 disc in Files, and follow the import prompts. See [Updates](#updates) before updating the app.

The result remains **Melee PC 0.4.2, build 54**. A successful cloud build confirms compilation and packaging; it does not confirm LiveContainer saves. The build downloads the latest published Melee PC recipe each time. A private imported copy does not have a **Sync fork** button; to pick up future PadMint workflow changes, import a fresh private copy under a new name.

## Build with PadMint

You need an **Apple Silicon Mac (M1 or newer)**, full **Xcode with its iOS platform**, **Rustup**, an internet connection and **15 GB of free space**. This section is for a local Mac build. From Windows, Linux, an Intel Mac or a phone browser, use the [GitHub route](#build-on-github-without-a-mac) above.

1. Install Xcode, open it once to finish setup, and select its command-line tools in **Xcode → Settings → Locations**. Install the **iOS** platform in **Settings → Components** if missing.
2. [Install Rustup](https://rustup.rs/) if it is not already installed. PadMint shows the setup command and a **Check again** button. The recipe installs the pinned Rust 1.96.0 iPhone compiler automatically.
3. Download **PadMint 0.5.22 or newer** from [PadMint releases](https://github.com/chrissotraidis/padmint/releases/latest), unzip it, and open **PadMint.command** in the new folder. An older PadMint folder has an older game list.
4. Open **MeleePad → Build options → Melee PC**, or select **Melee PC** directly. Choose **iPhone/iPad** and follow the local setup/build steps, or **Build on GitHub** for the browser route. CMake, Ninja and the pinned GNU ARM64 compiler are downloaded automatically. The game file is selected in the app afterward.
5. Keep the resulting personal `.ipa` private. Install it with your own signing tool, or import it into your existing LiveContainer setup. When switching from another app, use a new data container and keep your existing container and saves intact. Saves are not migrated automatically.
6. Transfer your own **USA revision 2 (NTSC-U 1.02)** Melee disc image to Files on the phone. In the app, tap **Choose Disc** and select it. ISO, CISO and RVZ are supported by this recipe. Game assets are not included in the IPA.

The recipe version is **0.1.0**; the personal app identifies itself as **Melee PC 0.4.2, build 54**. It uses a separate bundle identifier so it can coexist with the upstream app.

## Updates

Rebuild through PadMint or the GitHub workflow to get the maintained recipe, then install over your existing Melee PC copy using the same signing identity and container. Back up your saves first. The upstream in-app updater can replace this version with an upstream build that does not include the maintained patches.

## Save compatibility

To check saving in your setup, choose **Yes** when asked to create Game Data. Confirm that creation finishes and the game continues. Then change **Options → Sound → music/sound balance**, back out to the main menu to let it save, close the game completely, and reopen it. The changed balance should still be there.

Use the balance slider for this check: the port's Stereo/Mono option is a temporary system setting and resets separately from the memory-card save. LiveContainer save creation and reloading still need confirmation; tracking: [MeleePad #53](https://github.com/chrissotraidis/meleepad/issues/53). Report the app build, device, iOS and LiveContainer versions, and which step failed; do not upload your disc, save, IPA or identity.key.

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
