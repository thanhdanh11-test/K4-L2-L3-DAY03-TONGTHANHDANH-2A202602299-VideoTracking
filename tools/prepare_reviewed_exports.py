"""Install original CVAT-export bytes; preserve previous artifacts and lock."""
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'evidence' / 'before-final-export'
ARCHIVE.mkdir(parents=True, exist_ok=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest_path = ROOT / 'evidence/pre-gold/clip_01/manifest.json'
manifest = json.loads(manifest_path.read_text())
assert digest(ROOT / 'evidence/pre-gold/clip_01/gt.txt') == manifest['sha256']
receipt = {'pre_gold_hash_verified': True, 'pre_gold_unchanged': manifest['sha256'], 'exports': []}
for clip in ('clip_01', 'clip_02'):
    target = ROOT / f'annotations/{clip}/gt.txt'
    previous = ARCHIVE / f'{clip}-gt.txt'
    if target.exists() and not previous.exists():
        shutil.copy2(target, previous)
    source = ROOT / f'annotations/{clip}-reviewed-mot.zip'
    with ZipFile(source) as archive:
        assert 'gt/gt.txt' in archive.namelist()
        assert not any(n.lower().endswith(('.jpg', '.png')) for n in archive.namelist())
        content = archive.read('gt/gt.txt')
    target.write_bytes(content)  # Exact CVAT bytes: no MOT-coordinate editing.
    receipt['exports'].append({'clip':clip, 'zip':str(source.relative_to(ROOT)),
        'target':str(target.relative_to(ROOT)), 'sha256':digest(target),
        'rows':len(content.splitlines()), 'save_images':False})

gold = ROOT / 'gold/clip_01/gt.txt'
provided = Path('/Users/macos/AIVIN_LAB/gold/clip01/gt.txt')
gold.parent.mkdir(parents=True, exist_ok=True)
if gold.exists():
    assert digest(gold) == digest(provided), 'Existing gold differs; do not overwrite'
else:
    shutil.copy2(provided, gold)
receipt['gold_sha256'] = digest(gold)
(ROOT / 'outputs/export_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
