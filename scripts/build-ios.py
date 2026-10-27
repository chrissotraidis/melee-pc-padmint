#!/usr/bin/env python3
"""Game-specific backend for PadMint. Only the resulting local IPA contains game code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import subprocess
import sys
import urllib.request
import zipfile

SOURCE_URL = 'https://github.com/999sian/melee-pc.git'
SOURCE_REVISION = '0fb0af3304d3469308b5574369a6ec86f145632f'
GCC_URL = ('https://github.com/messense/homebrew-macos-cross-toolchains/releases/'
           'download/v15.2.0/aarch64-unknown-linux-gnu-aarch64-darwin.tar.gz')
GCC_SHA256 = '0f224db36d8572489f09ed5bce39f189eee998f9ab4f8ea07f510d6c7078caa3'
RUST_VERSION = '1.96.0'


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def read(args, **kwargs):
    return subprocess.check_output([str(arg) for arg in args], text=True, **kwargs).strip()


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        parser.error('This recipe currently requires an Apple Silicon Mac and full Xcode.')
    if not 1 <= args.jobs <= 16:
        parser.error('--jobs must be between 1 and 16')
    recipe = Path(__file__).resolve().parents[1]
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    sdk = read(['xcrun', '--sdk', 'iphoneos', '--show-sdk-path'])
    sdk_version = read(['xcrun', '--sdk', 'iphoneos', '--show-sdk-version'])
    rustup = shutil.which('rustup')
    if not rustup:
        fallback = Path.home() / '.cargo/bin/rustup'
        if fallback.is_file():
            rustup = str(fallback)
    if not rustup:
        parser.error('Install Rustup, then run the PadMint build again.')
    run([rustup, 'toolchain', 'install', RUST_VERSION, '--profile', 'minimal',
         '--target', 'aarch64-apple-ios'])
    rustc = read([rustup, 'which', '--toolchain', RUST_VERSION, 'rustc'])
    cargo = read([rustup, 'which', '--toolchain', RUST_VERSION, 'cargo'])

    source = work / 'source'
    if not source.exists():
        run(['git', 'clone', '--filter=blob:none', '--no-checkout', SOURCE_URL, source])
        run(['git', '-C', source, 'checkout', '--detach', SOURCE_REVISION])
    if read(['git', '-C', source, 'rev-parse', 'HEAD']) != SOURCE_REVISION:
        raise ValueError('Existing source revision differs; preserve it and use a new PadMint workspace.')
    patches = sorted((recipe / 'patches').glob('*.patch'))
    patch_identity = {patch.name: digest(patch) for patch in patches}
    stamp = work / 'applied-patches.json'
    if stamp.exists():
        if json.loads(stamp.read_text()) != patch_identity:
            raise ValueError('Patch inputs changed; use a new PadMint workspace.')
        run(['git', '-C', source, 'apply', '--reverse', '--check', *patches])
    else:
        if read(['git', '-C', source, 'status', '--porcelain']):
            raise ValueError('Downloaded source has local changes; refusing to reset them.')
        run(['git', '-C', source, 'apply', '--check', *patches])
        run(['git', '-C', source, 'apply', *patches])
        stamp.write_text(json.dumps(patch_identity, indent=2) + '\n')

    archive = work / 'gcc-15.2.0.tar.gz'
    if not archive.is_file() or digest(archive) != GCC_SHA256:
        print('Downloading the pinned GNU ARM64 compiler (184 MiB)…', flush=True)
        partial = archive.with_suffix('.partial')
        with urllib.request.urlopen(GCC_URL) as response, partial.open('wb') as output:
            shutil.copyfileobj(response, output)
        if digest(partial) != GCC_SHA256:
            raise ValueError('GNU compiler download checksum mismatch')
        partial.replace(archive)
    toolchain = work / 'toolchain'
    compiler = toolchain / 'aarch64-unknown-linux-gnu/bin/aarch64-unknown-linux-gnu-gcc'
    if not compiler.is_file():
        toolchain.mkdir(exist_ok=True)
        run(['/usr/bin/tar', '-xzf', archive, '-C', toolchain])
    env = dict(os.environ, IOS_SDK_PATH=sdk, IPHONEOS_DEPLOYMENT_TARGET='14.0',
               GCC_AARCH64_BIN=str(recipe / 'scripts/gcc-for-ios.py'),
               MELEE_GNU_COMPILER=str(compiler), RUSTUP_TOOLCHAIN=RUST_VERSION,
               CARGO_HOME=str(work / 'cargo'))
    env['PATH'] = str(Path(rustc).parent) + os.pathsep + env.get('PATH', '')
    build = work / 'build-ios'
    configure = ['cmake', '-S', source, '-B', build, '-G', 'Ninja',
                 '-DCMAKE_SYSTEM_NAME=iOS', '-DIOS=ON', '-DCMAKE_SYSTEM_PROCESSOR=arm64',
                 '-DCMAKE_OSX_ARCHITECTURES=arm64', '-DCMAKE_OSX_SYSROOT=' + sdk,
                 '-DCMAKE_OSX_DEPLOYMENT_TARGET=14.0', '-DCMAKE_BUILD_TYPE=Release',
                 '-DCMAKE_C_COMPILER=/usr/bin/clang', '-DCMAKE_CXX_COMPILER=/usr/bin/clang++',
                 '-DRust_CARGO_TARGET=aarch64-apple-ios', '-DRust_COMPILER=' + rustc,
                 '-DRust_CARGO=' + cargo, '-DAURORA_DAWN_PROVIDER=package',
                 '-DAURORA_SDL3_PROVIDER=vendor', '-DAURORA_SDL3_LINKAGE=static',
                 '-DAURORA_NOD_PROVIDER=vendor', '-DAURORA_CACHE_USE_ZSTD=OFF',
                 '-DBUILD_SHARED_LIBS=OFF', '-DPNG_SHARED=OFF', '-DPNG_STATIC=ON',
                 '-DCOMPILER_SUPPORTS_FOBJC_ARC=ON', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',
                 '-DCMAKE_DISABLE_FIND_PACKAGE_PkgConfig=TRUE',
                 '-DCMAKE_DISABLE_FIND_PACKAGE_PNG=TRUE',
                 '-DCMAKE_DISABLE_FIND_PACKAGE_Freetype=TRUE']
    configure += ['-DAURORA_ENABLE_' + component + '=ON'
                  for component in ('GX', 'DVD', 'CARD', 'THP', 'RMLUI')]
    run(configure, env=env)
    run(['cmake', '--build', build, '--target', 'melee', '-j', args.jobs], env=env)

    # Stage only declared program/resources, never copy a developer's app, data or profile.
    payload = args.output.parent / 'Payload'
    app = payload / 'Melee.app'
    app.mkdir(parents=True, exist_ok=False)
    binary = build / 'melee'
    if not binary.is_file():
        binary = build / 'melee.app/melee'
    shutil.copy2(binary, app / 'melee')
    shutil.copytree(source / 'resources', app / 'game-resources')
    with (source / 'platforms/ios/Info.plist').open('rb') as stream:
        info = plistlib.load(stream)
    for key in list(info):
        if key.startswith('DT') or key == 'BuildMachineOSBuild':
            del info[key]
    info.update(CFBundleShortVersionString='0.4.2', CFBundleVersion='54',
                DTPlatformName='iphoneos', DTPlatformVersion=sdk_version,
                DTSDKName='iphoneos' + sdk_version)
    with (app / 'Info.plist').open('wb') as stream:
        plistlib.dump(info, stream)
    shutil.copytree(source / 'licenses', app / 'notices/upstream')
    (app / 'notices/Aurora-LICENSE').write_bytes((source / 'extern/aurora/LICENSE').read_bytes())
    provenance = {'source_url': SOURCE_URL, 'source_revision': SOURCE_REVISION,
                  'patches': patch_identity, 'sdk': sdk_version,
                  'rust': RUST_VERSION, 'gcc_archive_sha256': GCC_SHA256,
                  'recipe_revision': read(['git', '-C', recipe, 'rev-parse', 'HEAD']),
                  'containsCompiledGameCode': True, 'publication': 'personal-only',
                  'executable_sha256': digest(app / 'melee')}
    (app / 'PersonalBuild.json').write_text(json.dumps(provenance, indent=2) + '\n')
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as ipa:
        for path in sorted(payload.rglob('*')):
            if path.is_file():
                ipa.write(path, path.relative_to(payload.parent))
    print('Personal unsigned IPA: ' + str(args.output), flush=True)
    print('Sign/install your copy, then import your own USA revision 2 disc. Keep the IPA private.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
