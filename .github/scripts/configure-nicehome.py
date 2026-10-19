"""Apply public server defaults only to this CI checkout, including its submodule."""
import base64
import json
import os
import re
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
