"""Which AIE tiles an xclbin's PDIs configure, and which cores share a program image (hash of program-memory writes).
CDO v2 module-1 records: 0x102 mask write (addr, mask, value), 0x103 write (addr, value), 0x105 DMA write
(addr_hi, addr_lo, data...), 0x107 mask write64 (hi, lo, mask, value), 0x108 write64 (hi, lo, value), 0x111 nop;
any other id is skipped by its length and counted.
Usage: layout.py <xclbin> [...]"""
import collections, hashlib, os, struct, subprocess, sys, tempfile

MAGIC = 0x004F4443


def tile_of(addr):
    return (addr >> 25) & 0x7F, (addr >> 20) & 0x1F, addr & 0xFFFFF


def records(w, unknown):
    i = 0
    while i < len(w):
        h = w[i]
        rid, n = h & 0xFFFF, (h >> 16) & 0xFF
        if n == 0xFF:
            i += 1
            n = w[i]
        a = w[i + 1:i + 1 + n]
        if rid == 0x103:
            yield a[0], a[1]
        elif rid == 0x102:
            yield a[0], a[2]
        elif rid == 0x108:
            yield a[1], a[2]
        elif rid == 0x107:
            yield a[1], a[3]
        elif rid == 0x105:
            for k, v in enumerate(a[2:]):
                yield a[1] + 4 * k, v
        elif rid != 0x111:
            unknown[hex(rid)] += 1
        i += 1 + n


def cdo_words(raw):
    w = struct.unpack(f"<{len(raw) // 4}I", raw[:len(raw) // 4 * 4])
    for i in range(1, len(w) - 3):
        if w[i] == MAGIC:
            n = w[i + 2]
            yield w[i + 4:i + 4 + n]


for x in sys.argv[1:]:
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["/opt/xilinx/xrt/bin/xclbinutil", "-i", os.path.abspath(x), "--dump-section",
                        "AIE_PARTITION:JSON:p.json", "--force"], capture_output=True, check=True, cwd=td)
        raws = [open(os.path.join(td, f), "rb").read() for f in sorted(os.listdir(td)) if f.endswith(".pdi")]
    unknown, tiles, pm, nrec, nstreams = collections.Counter(), collections.Counter(), collections.defaultdict(list), 0, 0
    for raw in raws:
        for ws in cdo_words(raw):
            nstreams += 1
            for addr, val in records(ws, unknown):
                nrec += 1
                c, row, off = tile_of(addr)
                tiles[(c, row)] += 1
                if row >= 2 and 0x20000 <= off < 0x30000:
                    pm[(c, row)].append((off, val))
    cls = collections.defaultdict(list)
    for t, v in pm.items():
        cls[hashlib.sha1(repr(sorted(v)).encode()).hexdigest()[:8]].append(t)
    print(f"== {os.path.basename(x)}: {len(raws)} PDIs, {nstreams} CDO streams, {nrec} writes, {len(tiles)} tiles, "
          f"{len(pm)} cores with program writes, unknown records {dict(unknown)}")
    for h, ts in sorted(cls.items(), key=lambda kv: min(kv[1])):
        cols = sorted({c for c, _ in ts})
        rows = sorted({r for _, r in ts})
        print(f"   program {h}: {len(ts):2d} cores, columns {cols}, rows {rows}, {len(pm[ts[0]])} PM words")
