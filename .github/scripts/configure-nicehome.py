"""Apply public server defaults only to this CI checkout, including its submodule."""
import base64
import json
import os
import re
import shutil
from pathlib import Path

values = {
    'custom-rendezvous-server': os.environ['ID_SERVER'].strip(),
    'relay-server': os.environ['RELAY_SERVER'].strip(),
    'api-server': os.environ['API_SERVER'].strip(),
    'key': os.environ['PUBLIC_KEY'].strip(),
}
for name in ('custom-rendezvous-server', 'relay-server'):
    if not re.fullmatch(r'[A-Za-z0-9.-]+:[0-9]{1,5}', values[name]):
        raise ValueError(f'{name}: expected hostname:port')
    port = int(values[name].rsplit(':', 1)[1])
    if not 1 <= port <= 65535:
        raise ValueError(f'{name}: invalid port')
if not re.fullmatch(r'https://[A-Za-z0-9.-]+(?::[0-9]{1,5})?', values['api-server']):
    raise ValueError('API_SERVER: expected HTTPS origin without trailing slash')
if len(base64.b64decode(values['key'], validate=True)) != 32:
    raise ValueError('PUBLIC_KEY must encode 32 bytes')

source = Path('libs/hbb_common/src/config.rs')
text = source.read_text()
anchor = 'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = Default::default();'
if text.count(anchor) != 1:
    raise ValueError('Upstream DEFAULT_SETTINGS changed; review customization before building')
entries = ',\n'.join(f'        ({json.dumps(k)}.to_owned(), {json.dumps(v)}.to_owned())' for k, v in values.items())
text = text.replace(anchor, 'pub static ref DEFAULT_SETTINGS: RwLock<HashMap<String, String>> = RwLock::new(HashMap::from([\n' + entries + '\n    ]));')
text, count = re.subn(r'pub const RS_PUB_KEY: &str = "[^"]*";', lambda _: 'pub const RS_PUB_KEY: &str = ' + json.dumps(values['key']) + ';', text)
if count != 1:
    raise ValueError('Upstream RS_PUB_KEY changed; review customization before building')
source.write_text(text)
print('Applied public server defaults; no account credentials embedded.')

# Branding is applied only by this manual Windows workflow.
brand = os.environ.get('BRAND', 'interlogic').strip()
if not re.fullmatch(r'[A-Za-z0-9_-]+', brand):
    raise ValueError('BRAND must contain only letters, digits, "-" or "_"')

branding_root = Path(__file__).resolve().parents[1] / 'branding'
branding = branding_root / brand
if not branding.is_dir():
    available = sorted(p.name for p in branding_root.iterdir() if p.is_dir())
    raise ValueError(f'Unknown brand "{brand}". Available: {", ".join(available) or "(none found)"}')

app_name = os.environ.get('APP_NAME', 'Interlogic Support').strip()
if not app_name:
    raise ValueError('APP_NAME must not be empty')

app_anchor = 'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());'
text = source.read_text()
if text.count(app_anchor) != 1:
    raise ValueError('Upstream APP_NAME changed; review branding')
text = text.replace(app_anchor, 'pub static ref APP_NAME: RwLock<String> = RwLock::new(' + json.dumps(app_name) + '.to_owned());')

rc_path = Path('flutter/windows/runner/Runner.rc')
rc = rc_path.read_text()
for field, old, new in (
    ('CompanyName', 'Purslane Tech Pte. Ltd.', 'Interlogic'),
    ('FileDescription', 'RustDesk Remote Desktop', app_name),
    ('ProductName', 'RustDesk', app_name),
):
    old_value = f'VALUE "{field}", "{old}"'
    if rc.count(old_value) != 1:
        raise ValueError(f'Upstream Windows resource {field} changed; review branding')
    rc = rc.replace(old_value, f'VALUE "{field}", "{new}"')

for asset in ('logo.png', 'icon.png', 'icon.ico'):
    if not (branding / asset).is_file():
        raise ValueError(f'Missing branding asset for brand "{brand}": {asset}')

source.write_text(text)
rc_path.write_text(rc)

for target in ('res/icon.ico', 'res/tray-icon.ico', 'flutter/windows/runner/resources/app_icon.ico'):
    shutil.copyfile(branding / 'icon.ico', target)
for target in ('res/icon.png', 'flutter/assets/icon.png'):
    shutil.copyfile(branding / 'icon.png', target)
shutil.copyfile(branding / 'icon.ico', 'flutter/assets/icon.ico')
for filename in ('logo.png', 'logo_light.png', 'logo_dark.png'):
    shutil.copyfile(branding / 'logo.png', Path('flutter/assets') / filename)

print(f'Applied "{brand}" branding ("{app_name}"); upstream license/copyright retained.')
