"""Check tracked source provenance, local Markdown links, and common secret patterns.

This bounded pattern check is not a complete security audit. No secret contents
are printed. Checks tracked working-tree files. Use --staged to inspect
index blobs rather than potentially newer working-tree contents before commit.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    staged = '--staged' in sys.argv
    def read_bytes(name):
        if staged:
            return subprocess.run(['git', 'show', ':' + name], cwd=ROOT,
                                  capture_output=True, check=True).stdout
        return (ROOT / name).read_bytes()
    manifest = json.loads(read_bytes('docs/references/SOURCE_MANIFEST.json').decode('utf-8'))
    for entry in manifest['files']:
        path = ROOT / entry['path']
        if not path.is_file() or hashlib.sha256(read_bytes(entry['path'])).hexdigest() != entry['sha256']:
            errors.append('Original SHA-256 mismatch: ' + entry['path'])
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True)
    paths = [p for p in result.stdout.decode('utf-8').split('\0') if p]
    if not paths:
        errors.append('No tracked files; stage the intended commit first.')
    # Intentionally report file/line only, never a matching value.
    patterns = [re.compile(r'gh[pousr]_[A-Za-z0-9]{25,}'),
                re.compile(r'github_pat_[A-Za-z0-9_]{40,}'),
                re.compile(r'sk-[A-Za-z0-9_-]{24,}'),
                re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    for name in paths:
        path = ROOT / name
        relative_parts = Path(name).parts
        if (path.name.startswith('.env') and path.name != '.env.example') or (
            relative_parts[0] == 'analysis' or any(
                part in {'node_modules', '.venv', '__pycache__'} for part in relative_parts
            )
        ):
            errors.append('Forbidden tracked path: ' + name)
        if path.suffix.lower() in {'.pdf', '.png', '.jpg', '.zip'}:
            continue
        try:
            text = read_bytes(name).decode('utf-8')
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if any(pattern.search(line) for pattern in patterns):
                errors.append(f'Possible secret: {name}:{i}')
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                link = link.strip('<>')
                if re.match(r'^[a-zA-Z][\w+.-]*:', link) or link.startswith(('#', '/')):
                    continue
                target = unquote(link.split('#', 1)[0])
                if target and not (path.parent / target).exists():
                    errors.append(f'Broken local link: {name} -> {target}')
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print(f'PASS ({"index" if staged else "working tree"}): {len(manifest["files"])} original hashes; {len(paths)} tracked paths; local links and bounded secret-pattern check.')
    print('Not a full secret, license, dependency, demo runtime, or financial validity audit.')


if __name__ == '__main__':
    main()
