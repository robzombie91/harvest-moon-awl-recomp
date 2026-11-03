#!/usr/bin/env python3
"""Conservative initial PPC function candidates for GameCube RELs.

Produces gcn-recomp REL_SYMBOLS files without modifying the project.
Sources: REL prolog/epilog/unresolved, executable-section entry, local BL
instructions, and relocation targets referencing executable sections.
These are heuristic symbol maps, NOT verified function boundaries.
"""
import argparse
import struct
from collections import Counter
from pathlib import Path


def u32(buf, pos):
    return struct.unpack_from('>I', buf, pos)[0]


def signed26(n):
    return n - 0x4000000 if n & 0x2000000 else n


def candidates_from_file(path):
    data = path.read_bytes()
    if len(data) < 0x4C:
        raise ValueError(f'{path}: too small for REL header')
    modid = u32(data, 0)
    count, table, version = u32(data, 0x0C), u32(data, 0x10), u32(data, 0x1C)
    if not 1 <= count <= 128 or table + count * 8 > len(data):
        raise ValueError(f'{path}: invalid REL section table')
    sections = []
    for idx in range(count):
        w0, size = struct.unpack_from('>II', data, table + 8 * idx)
        off, executable = w0 & ~1, bool(w0 & 1)
        if off and off + size > len(data):
            raise ValueError(f'{path}: section {idx} exceeds REL file')
        sections.append((off, size, executable))
    starts = [set() for _ in sections]
    source = [Counter() for _ in sections]

    def add(idx, pos, reason):
        if idx >= len(sections):
            return
        off, size, executable = sections[idx]
        if not executable or pos % 4 or pos < 0 or pos >= size:
            return
        starts[idx].add(pos)
        source[idx][reason] += 1

    for idx, (off, size, executable) in enumerate(sections):
        if not executable or not off:
            continue
        add(idx, 0, 'section entry')
        for pos in range(0, size - 3, 4):
            insn = u32(data, off + pos)
            # PPC b/bl opcode 18, relative, with link bit on.
            if (insn >> 26) == 18 and (insn & 3) == 1:
                target = pos + signed26(insn & 0x03FFFFFC)
                add(idx, target, 'local bl')

    # Header entry points. REL prolog offset is *within* its section.
    for idx, pos, label in (
        (data[0x30], u32(data, 0x34), '_prolog'),
        (data[0x31], u32(data, 0x38), '_epilog'),
        (data[0x32], u32(data, 0x3C), '_unresolved'),
    ):
        if idx:
            add(idx, pos, label)

    # REL relocation streams. Only same-module relocation targets identify
    # addresses in the module's own executable sections. Other-module refs
    # are handled when analyzing that other module.
    imp_offset, imp_size = u32(data, 0x28), u32(data, 0x2C)
    if imp_offset + imp_size > len(data) or imp_size % 8:
        raise ValueError(f'{path}: invalid relocation import table')
    for k in range(imp_size // 8):
        imported_id, reloc_pos = struct.unpack_from('>II', data, imp_offset + k * 8)
        if imported_id != modid:
            continue
        for _ in range(1000000):
            if reloc_pos + 8 > len(data):
                raise ValueError(f'{path}: invalid relocation stream')
            delta, typ, target_sec, addend = struct.unpack_from('>HBBI', data, reloc_pos)
            reloc_pos += 8
            if typ == 203:  # R_DOLPHIN_END
                break
            if typ in (201, 202):  # NOP, SECTION
                continue
            if typ in (1, 2, 3, 4, 5, 6, 7, 10, 11, 26):
                add(target_sec, addend, 'self relocation target')
        else:
            raise ValueError(f'{path}: unterminated relocation stream')

    return modid, version, sections, starts, source


def generate(paths, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for path in paths:
        modid, version, sections, starts, source = candidates_from_file(path)
        prefix = path.stem
        symbol_lines = [f'// Provisional REL symbols for {path.name} (module {modid}, version {version})',
                        '// Function starts inferred from PPC calls, REL relocations, and module entry points.',
                        '// REVIEW REQUIRED: function sizes and start addresses are heuristic.']
        split_lines = ['Sections:']
        summary = []
        for idx, (off, size, exe) in enumerate(sections):
            if not size:
                continue
            secname = f'.s{idx}'
            kind = 'code' if exe else ('bss' if off == 0 else 'data')
            split_lines.append(f'\t{secname} type:{kind} align:4')
            if not exe:
                continue
            ordered = sorted(starts[idx])
            summary.append(f'  section {idx}: {len(ordered)} candidates, size {size:#x}, sources {dict(source[idx])}')
            for j, start in enumerate(ordered):
                end = ordered[j + 1] if j + 1 < len(ordered) else size
                if end <= start:
                    continue
                name = f'fn_{modid}_{idx}_{start:06X}'
                if idx == path.read_bytes()[0x30] and start == u32(path.read_bytes(), 0x34):
                    name = '_prolog'
                elif idx == path.read_bytes()[0x31] and start == u32(path.read_bytes(), 0x38):
                    name = '_epilog'
                elif idx == path.read_bytes()[0x32] and start == u32(path.read_bytes(), 0x3C):
                    name = '_unresolved'
                symbol_lines.append(f'{name} = {secname}:0x{start:X}; // type:function size:0x{end-start:X}')
        (dest / f'{prefix}.txt').write_text('\n'.join(symbol_lines) + '\n')
        (dest / f'{prefix}.splits.txt').write_text('\n'.join(split_lines) + '\n')
        print(f'{path.name}: module {modid} REL v{version}')
        for line in summary:
            print(line)
        print('  saved:', dest / f'{prefix}.txt')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path, help='Extracted .rel files')
    parser.add_argument('-o', '--output', type=Path, default=Path('analysis/rel-symbols'))
    args = parser.parse_args()
    generate(args.files, args.output)


if __name__ == '__main__':
    main()
