import subprocess
import sys

sdk = subprocess.check_output(['xcrun', '--show-sdk-path']).decode().strip()

with open('libs/scrap/build.rs', 'r') as f:
    content = f.read()

old = '    b.generate().unwrap().write_to_file(ffi_rs).unwrap();'
new = (
    '    // macOS arm64: explicit target for bindgen\n'
    '    if std::env::var("CARGO_CFG_TARGET_OS").unwrap_or_default() == "macos"\n'
    '        && std::env::var("CARGO_CFG_TARGET_ARCH").unwrap_or_default() == "aarch64"\n'
    '    {\n'
    '        b = b.clang_arg("--target=arm64-apple-macos");\n'
    '        b = b.clang_arg("-mmacosx-version-min=14.0");\n'
    f'        b = b.clang_arg("-isysroot{sdk}");\n'
    f'        b = b.clang_arg("-I{sdk}/usr/include");\n'
    '    }\n'
    '    b.generate().unwrap().write_to_file(ffi_rs).unwrap();'
)

if old in content:
    content = content.replace(old, new)
    with open('libs/scrap/build.rs', 'w') as f:
        f.write(content)
    print('=== Patch applied successfully ===')
else:
    print('ERROR: target string not found!')
    for i, line in enumerate(content.split('\n')):
        if 'generate' in line:
            print(f'Line {i}: {repr(line)}')
    sys.exit(1)