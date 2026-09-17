#!/usr/bin/env python3
"""Generate a 24-frame run cycle for my_xue.blend (mouse) by injecting BezTriple keys.
Pure-python .blend editing, no Blender required.
"""
import struct, math, os

SRC = '/workspace/attachments/my_xue.blend'
DST = '/workspace/my_xue_run.blend'

import json as _json
# v3: motion retargeted from reference glTF mouse (sketchfab charliecatling
# Mouse rig|run cycle, 0.458s bound/gallop). Resampled uniform keys.
with open('/workspace/refmouse/resampled.json') as _f:
    _R = _json.load(_f)
FRAMES = _R['frames']  # 24 fractional frames 1.0..11.54
FRAME_START = 1.0
FRAME_END = 12.0
_N = len(FRAMES)
_D2R = math.pi/180.0
def _dm(key):
    v = _R['pitch'][key]
    m = sum(v)/len(v)
    return [x-m for x in v]
# per-bone pitch curves in radians: base + gain * demeaned-ref
_P = {}
_P['hindleg.upper.L'] = [0.12 + _D2R*0.30*x for x in _dm('DEF-thigh.L_0124')]
_P['hindleg.upper.R'] = [0.12 + _D2R*0.30*x for x in _dm('DEF-thigh.R_0149')]
_P['hindleg.lower.L'] = [0.55 + _D2R*0.45*x for x in _dm('DEF-shin.L_0126')]
_P['hindleg.lower.R'] = [0.55 + _D2R*0.40*x for x in _dm('DEF-shin.R_0151')]
_P['frontleg.upper.L'] = [-0.05 + _D2R*0.70*x for x in _dm('DEF-front_thigh.L_0207')]
_P['frontleg.upper.R'] = [-0.05 + _D2R*0.70*x for x in _dm('DEF-front_thigh.R_0249')]
_P['frontleg.lower.L'] = [0.50 + _D2R*0.40*x for x in _dm('DEF-front_shin.L_0209')]
_P['frontleg.lower.R'] = [0.50 + _D2R*0.35*x for x in _dm('DEF-front_shin.R_0251')]
_P['hip.L'] = [0.30*x for x in _P['hindleg.upper.L']]
_P['hip.R'] = [0.30*x for x in _P['hindleg.upper.R']]
_P['Bone'] = [0.30*x for x in _P['frontleg.upper.L']]
_P['Bone.006'] = [0.30*x for x in _P['frontleg.upper.R']]
_P['torso'] = [_D2R*0.50*x for x in _dm('torso_030')]
_P['spine'] = [_D2R*0.40*x for x in _dm('torso_030')]
_P['spine.001'] = [_D2R*0.50*x for x in _dm('hips_031')]
_P['head'] = [_D2R*0.40*x for x in _dm('head_0164')]
_P['neck'] = [0.5*x for x in _P['head']]
_P['tail.4'] = [_D2R*0.50*x for x in _dm('DEF-spine.003_059')]
_P['tail.3'] = [_D2R*0.50*x for x in _dm('DEF-spine.002_058')]
_P['tail.2'] = [_D2R*0.50*x for x in _dm('DEF-spine.001_057')]
_P['tail.1'] = list(_P['tail.2'])
_P['tail.tip'] = list(_P['tail.2'])
_P['ear.R'] = [0.05 + _D2R*0.50*x for x in _dm('ear.R_014')]
_P['ear.L'] = [0.05 + _D2R*0.50*x for x in _dm('ear.L_017')]
# root surge (fwd Y) from ref torso Z, bob (up Z) from ref hips Y, scaled
_TZ = _R['trans']['torso_030']
_HY = _R['trans']['hips_031']
_TX = _R['trans']['torso_030']
_mz = sum(p[2] for p in _TZ)/len(_TZ)
_my = sum(p[1] for p in _HY)/len(_HY)
_mx = sum(p[0] for p in _TX)/len(_TX)
_S = 0.24  # size ratio ours/ref (length 1.17/4.9)
_ROOT_Y = [(p[2]-_mz)*_S for p in _TZ]
_ROOT_Z = [(p[1]-_my)*_S for p in _HY]
_ROOT_X = [(p[0]-_mx)*_S for p in _TX]
_FIDX = {fr:i for i,fr in enumerate(FRAMES)}

def qx(a):
    return (math.cos(a/2), math.sin(a/2), 0.0, 0.0)
def qy(a):
    return (math.cos(a/2), 0.0, math.sin(a/2), 0.0)
def qz(a):
    return (math.cos(a/2), 0.0, 0.0, math.sin(a/2))
def qmul(q1, q2):
    w1,x1,y1,z1 = q1
    w2,x2,y2,z2 = q2
    return (
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    )

TAIL_ORDER = ['tail.4','tail.3','tail.2','tail.1','tail.tip']

def bone_angle(bone, frame):
    """Return quaternion (w,x,y,z) for bone at frame, and loc (x,y,z)."""
    # v3: reference-driven (see tables above). frame must be in FRAMES.
    ki = _FIDX.get(frame)
    if ki is None:
        # nearest (should not happen)
        ki = min(range(_N), key=lambda i: abs(FRAMES[i]-frame))
    th = 0.0
    th2 = 0.0
    if bone == 'spine.001':
        loc = (_ROOT_X[ki], _ROOT_Y[ki], _ROOT_Z[ki])
        q = qx(_P['spine.001'][ki])
    elif bone in _P:
        q = qx(_P[bone][ki])
        loc = (0.0, 0.0, 0.0)
    elif bone == 'MoustacheBone':
        q = qz(0.20*_P['head'][ki] + 0.02*math.sin(ki*2.3))
        loc = (0.0, 0.0, 0.0)
    else:
        q = (1.0,0.0,0.0,0.0)
        loc = (0.0, 0.0, 0.0)
    return q, loc

# --- read file ---
with open(SRC,'rb') as f:
    blob = bytearray(f.read())

header = bytes(blob[:12])
assert header == b'BLENDER-v306', header

# parse blocks
blocks = []  # (pos, code, size, mem, sdna, count, ds)
pos = 12
while True:
    code = bytes(blob[pos:pos+4])
    size = struct.unpack('<I', blob[pos+4:pos+8])[0]
    mem = struct.unpack('<Q', blob[pos+8:pos+16])[0]
    sdna = struct.unpack('<I', blob[pos+16:pos+20])[0]
    count = struct.unpack('<I', blob[pos+20:pos+24])[0]
    ds = pos+24
    blocks.append([pos, code, size, mem, sdna, count, ds])
    if code == b'ENDB':
        break
    pos = ds + size

print(f"total blocks: {len(blocks)}")

# load DNA to map sdna idx -> typename
import pickle
with open('/workspace/.blender/dna.pkl','rb') as inf:
    names, types, tlens, strcs = pickle.load(inf)

def typename(sdna):
    return types[strcs[sdna][0]]

# find DNA1 and ENDB positions
dna_block = None
endb_block = None
for b in blocks:
    if b[1] == b'DNA1':
        dna_block = b
    if b[1] == b'ENDB':
        endb_block = b
assert dna_block is not None

# find Action block
ac_blocks = [b for b in blocks if b[1]==b'AC\x00\x00']
print(f"Action blocks: {len(ac_blocks)}")
for b in ac_blocks:
    ds = b[6]
    raw = bytes(blob[ds+40:ds+40+66]).split(b'\x00')[0].decode()
    print(f"  {raw} mem={hex(b[3])}")

# build mem map
mem_to_block = {b[3]: b for b in blocks if b[3]!=0}

# find FCurve blocks
fcurve_blocks = [b for b in blocks if b[1]==b'DATA' and typename(b[4])=='FCurve']
print(f"FCurves: {len(fcurve_blocks)}")

# find BezTriple sdna idx
bezt_sdna = None
for idx,(ti,_) in enumerate(strcs):
    if types[ti]=='BezTriple':
        bezt_sdna = idx
        break
print(f"BezTriple sdna={bezt_sdna}")

# resolve rna_path for each fcurve
import re
def get_rna(fb):
    ds = fb[6]
    rna_ptr = struct.unpack('<Q', blob[ds+88:ds+96])[0]
    b2 = mem_to_block.get(rna_ptr)
    if b2 is None:
        # search inside
        for bb in blocks:
            if bb[3]!=0 and bb[3]<=rna_ptr<bb[3]+bb[2]:
                off = rna_ptr-bb[3]
                raw = bytes(blob[bb[6]+off:bb[6]+bb[2]])
                return raw.split(b'\x00')[0].decode()
        return f"?{hex(rna_ptr)}"
    raw = bytes(blob[b2[6]:b2[6]+b2[2]])
    return raw.split(b'\x00')[0].decode()

# update Action frame range
for b in ac_blocks:
    ds = b[6]
    struct.pack_into('<f', blob, ds+272, FRAME_START)
    struct.pack_into('<f', blob, ds+276, FRAME_END)

# prepare new BezTriple blocks
new_blocks_data = []  # list of (mem, count, data bytes)
NEXT_MEM = 0x7f7f00000000
def alloc_mem(size):
    global NEXT_MEM
    m = NEXT_MEM
    NEXT_MEM += 0x1000
    return m

# BezTriple template constants from original
IPO_BEZ = 2
H_AUTO = 4
F_SEL = 1
BACK = 1.7015800476074219
AMP = 0.800000011920929
PERIOD = 4.099999904632568

def make_bezt(frame, value):
    # vec: h1(frame-1,val), key(frame,val), h2(frame+1,val)
    vec = (frame-1.0, value, 0.0, frame, value, 0.0, frame+1.0, value, 0.0)
    data = struct.pack('<9f', *vec)
    data += struct.pack('<3f', 0.0, 0.0, 0.0)  # alfa,weight,radius
    data += struct.pack('<B', IPO_BEZ)  # ipo
    data += struct.pack('<B', H_AUTO)   # h1
    data += struct.pack('<B', H_AUTO)   # h2
    data += struct.pack('<B', F_SEL)    # f1
    data += struct.pack('<B', F_SEL)    # f2
    data += struct.pack('<B', F_SEL)    # f3
    data += struct.pack('<b', 0)        # hide
    data += struct.pack('<b', 0)        # easing
    data += struct.pack('<3f', BACK, AMP, PERIOD)
    data += struct.pack('<b', 0)        # auto_handle_type
    data += b'\x00\x00\x00'             # _pad
    assert len(data)==72
    return data

rna_re = re.compile(r'pose\.bones\["([^"]+)"\]\.(location|rotation_quaternion)')

n_updated = 0
for fb in fcurve_blocks:
    ds = fb[6]
    rna = get_rna(fb)
    ai = struct.unpack('<i', blob[ds+84:ds+88])[0]
    m = rna_re.match(rna)
    if not m:
        print(f"skip {rna}")
        continue
    bone, prop = m.group(1), m.group(2)
    # compute 5 values
    vals = []
    for fr in FRAMES:
        q, loc = bone_angle(bone, fr)
        if prop == 'location':
            vals.append(loc[ai])
        else:
            # quat order w,x,y,z -> ai 0..3
            vals.append(q[ai])
    # build new bezt block data (5 triples)
    payload = b''.join(make_bezt(fr, v) for fr, v in zip(FRAMES, vals))
    new_mem = alloc_mem(len(payload))
    new_blocks_data.append((new_mem, len(FRAMES), payload))
    # update FCurve in place
    struct.pack_into('<i', blob, ds+64, len(FRAMES))  # totvert
    struct.pack_into('<Q', blob, ds+48, new_mem)      # bezt ptr
    struct.pack_into('<Q', blob, ds+56, 0)            # fpt null
    struct.pack_into('<h', blob, ds+78, 2)            # extend = cyclic
    struct.pack_into('<f', blob, ds+72, vals[0])      # curval
    n_updated += 1

print(f"updated {n_updated} FCurves, new blocks {len(new_blocks_data)}")

# --- write new file: original up to DNA1, then new blocks, then DNA1+ENDB ---
# find file offset of DNA1 block start
dna_pos = dna_block[0]
# everything before dna_pos stays (with our in-place edits already in blob)
prefix = bytes(blob[:dna_pos])
dna_and_after = bytes(blob[dna_pos:])  # DNA1 + ENDB

out = bytearray()
out += prefix
for mem, cnt, payload in new_blocks_data:
    out += b'DATA'
    out += struct.pack('<I', len(payload))
    out += struct.pack('<Q', mem)
    out += struct.pack('<I', bezt_sdna)
    out += struct.pack('<I', cnt)
    out += payload
out += dna_and_after

with open(DST,'wb') as f:
    f.write(out)
print(f"wrote {DST} {len(out)} bytes (orig {len(blob)})")
