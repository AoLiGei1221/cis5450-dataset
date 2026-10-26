#!/usr/bin/env python3
"""Download the frozen raw data Release and verify SHA-256; standard library only."""
from pathlib import Path
import argparse, hashlib, json, time, urllib.request, zipfile

ROOT = Path(__file__).resolve().parents[1]

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def valid(path, row):
    return path.is_file() and path.stat().st_size==row.get('size_bytes',row.get('bytes')) and sha256(path)==row['sha256']

def download(row, path):
    path.parent.mkdir(parents=True,exist_ok=True)
    partial=path.with_name(path.name+'.part')
    if valid(path,row):
        print('Cached and verified:',path.name,flush=True);return
    for attempt in range(3):
        try:
            offset=partial.stat().st_size if partial.exists() else 0
            headers={'User-Agent':'cis5450-dataset/1.0'}
            if offset:headers['Range']=f'bytes={offset}-'
            with urllib.request.urlopen(urllib.request.Request(row['url'],headers=headers),timeout=120) as response:
                append=offset>0 and response.status==206
                if not append:offset=0
                done=offset;last=done
                with partial.open('ab' if append else 'wb') as f:
                    for block in iter(lambda:response.read(4*1024*1024),b''):
                        f.write(block);done+=len(block)
                        if done-last>=128*1024*1024:
                            print(f"  {row['asset']}: {done/1024**2:.0f}/{row['size_bytes']/1024**2:.0f} MiB",flush=True);last=done
            if not valid(partial,row):
                partial.unlink(missing_ok=True)
                raise ValueError('Downloaded size or SHA-256 differs from the pinned manifest')
            partial.replace(path);return
        except Exception:
            if attempt==2:raise
            time.sleep(2*(attempt+1))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',choices=['all','overture','osm','acs','tiger'],default='all')
    parser.add_argument('--dry-run',action='store_true',help='List pinned assets without downloading')
    parser.add_argument('--verify-only',action='store_true',help='Verify installed raw files; do not download')
    args=parser.parse_args()
    assets=json.loads((ROOT/'manifests/release_assets.json').read_text())['assets']
    raw=json.loads((ROOT/'manifests/raw_files.json').read_text())['files']
    prefixes={'overture':'data/raw/overture_ca/','osm':'data/raw/osm/','acs':'data/raw/census/acs2024/','tiger':'data/raw/census/tiger2024/'}
    for row in assets:
        if args.dataset not in ('all',row['dataset']):continue
        expected=[f for f in raw if f['path'].startswith(prefixes[row['dataset']])]
        if args.dry_run:
            print(row['dataset'],row['size_bytes'],'bytes',row['url']);continue
        if not args.verify_only and not all(valid(ROOT/f['path'],f) for f in expected):
            target=ROOT/'.downloads'/row['asset'] if row['kind']=='zip' else ROOT/row['destination']
            print('Downloading:',row['asset'],flush=True)
            download(row,target)
            if row['kind']=='zip':
                with zipfile.ZipFile(target) as z:
                    for member in z.infolist():
                        # Only data payloads are extracted; notices already ship with the clone.
                        if not member.filename.startswith('data/raw/'):continue
                        destination=(ROOT/member.filename).resolve()
                        if not destination.is_relative_to(ROOT.resolve()):raise ValueError('Unsafe archive member')
                        z.extract(member,ROOT)
        missing=[f['path'] for f in expected if not valid(ROOT/f['path'],f)]
        if missing:raise SystemExit('Missing or mismatched raw inputs: '+', '.join(missing))
        print(f"Verified {row['dataset']}: {len(expected)} files",flush=True)

if __name__=='__main__':main()
