import os
import re

SEP = chr(92)  # 反斜杠

files = []
for dp, dns, fns in os.walk('games'):
    dns[:] = [d for d in dns if d != '.git']
    for f in fns:
        files.append(os.path.join(dp, f).replace(SEP, '/'))
fileset = set(files)

lower_map = {}
for f in files:
    lower_map.setdefault(f.lower(), []).append(f)

text_ext = {'.html', '.htm', '.js', '.css', '.json'}
pat = re.compile(
    r'''["'(]([A-Za-z0-9_\-./''' + re.escape(SEP) + r''']+\.(?:js|css|json|png|jpg|jpeg|gif|svg|mp3|ogg|wav|fnt|woff2?|ttf|html|htm))["')]''',
    re.I,
)

refs = set()
checked = 0
for dp, dns, fns in os.walk('games'):
    for f in fns:
        if os.path.splitext(f)[1].lower() not in text_ext:
            continue
        p = os.path.join(dp, f)
        try:
            txt = open(p, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        checked += 1
        base = os.path.dirname(p).replace(SEP, '/')
        for m in pat.finditer(txt):
            raw = m.group(1).replace(SEP, '/')
            if raw.startswith('http') or raw.startswith('data:'):
                continue
            if raw.startswith('/'):
                target = raw.lstrip('/')
            else:
                target = os.path.normpath(os.path.join(base, raw)).replace(SEP, '/')
            refs.add((target, p))

missing, case_mismatch = [], []
for target, src in refs:
    if target in fileset:
        continue
    alt = lower_map.get(target.lower())
    if alt:
        case_mismatch.append((target, alt[0], src))
    else:
        missing.append((target, src))

print('扫描文本文件:', checked, '引用去重:', len(refs))
print('大小写不匹配:', len(case_mismatch))
for t, a, s in case_mismatch[:20]:
    print('  ref:', t, '-> 实际:', a, '来自:', s)
print('未找到(可能是动态拼接 / 运行时生成):', len(missing))
for t, s in missing[:12]:
    print('  ', t, '<-', s)
