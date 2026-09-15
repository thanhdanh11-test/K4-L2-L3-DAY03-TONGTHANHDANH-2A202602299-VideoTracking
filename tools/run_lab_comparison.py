"""Reproduce the notebook's fixed two-run comparison, retaining earlier outputs."""
import hashlib
import json
import os
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / 'outputs/tmp_lab_deps'))
os.environ['YOLO_CONFIG_DIR'] = str(ROOT / 'outputs/tmp_yolo_config')
import ultralytics
import torch
from importlib import metadata
from run_tracker import track_clip, write_mot

assert ultralytics.__version__ == '8.4.145'
assert metadata.version('lap') == '0.5.13'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


archive = ROOT / 'evidence/before-pinned-model-rerun'
archive.mkdir(parents=True, exist_ok=True)
prior = []
for name in ['model_bytetrack_clip_01.txt', 'model_reid_clip_01.txt',
             'model_run_config.json', 'eval_reid_vs_me.json']:
    source = ROOT / 'outputs' / name
    if source.exists():
        destination = archive / name
        if not destination.exists():
            shutil.copy2(source, destination)
        prior.append({'file':name,'mtime_utc':datetime.fromtimestamp(
            destination.stat().st_mtime,timezone.utc).isoformat(),'sha256':sha(destination)})
(archive / 'provenance.json').write_text(json.dumps(prior,indent=2)+'\n')

runs = {'bytetrack':{'label':'ByteTrack control','tracker':'bytetrack.yaml'},
        'reid':{'label':'BoT-SORT + ReID treatment','tracker':'configs/trackers/botsort-reid.yaml'}}
config = {'python':platform.python_version(),'ultralytics':ultralytics.__version__,
    'torch':torch.__version__,'lap':metadata.version('lap'),'weights':'yolo26n.pt',
    'weights_sha256':sha('yolo26n.pt'),'runs':runs,'conf':0.25,'iou':0.7,
    'imgsz':960,'classes':[2,5,7],'device':'cpu','persist':True,'clip_frames':190,
    'started_at_utc':datetime.now(timezone.utc).isoformat(),
    'annotation_sha256':sha('annotations/clip_01/gt.txt'),
    'pre_gold_sha256':sha('evidence/pre-gold/clip_01/gt.txt'),
    'historical_order_warning':'Earlier model file mtimes precede pre-gold manifest; preserved, not repaired by this rerun.'}
for name, run in runs.items():
    tracker_path = (Path(ultralytics.__file__).parent/'cfg/trackers/bytetrack.yaml'
                    if name == 'bytetrack' else ROOT/run['tracker'])
    run['tracker_yaml'] = tracker_path.read_text()
    run['tracker_sha256'] = sha(tracker_path)
    print(f'Starting {name} with ultralytics {ultralytics.__version__}',flush=True)
    rows = track_clip(ROOT/'data/clips/clip_01','yolo26n.pt',run['tracker'],
                      0.25,0.7,960,[2,5,7],'cpu')
    target = ROOT/f'outputs/model_{name}_clip_01.txt'
    write_mot(rows,target)
    run.update(rows=len(rows),tracks=len({r[1] for r in rows}),output_sha256=sha(target))
    print(f'{name}: {len(rows)} boxes, {run["tracks"]} tracks',flush=True)
config['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
(ROOT/'outputs/model_run_config.json').write_text(json.dumps(config,indent=2)+'\n')
