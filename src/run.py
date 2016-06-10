import codecs
import glob
import os
import re
import sys

ALL_CMDS = [
    'inbox', 'outbox',
    'copyto', 'copyfrom',
    'add', 'sub',
    'bumpup', 'bumpdn',
    'jump', 'jumpz', 'jumpn',
]

ALL_CMDS_PATTERN = u'|'.join(ALL_CMDS)


class Q:
    def __init__(self):
        self.cmds = set()  # allowed cmds
        self.mem = []

    def dump(self):
        print u'ALLOWED COMMANDS (total {}):'.format(len(self.cmds))
        for cmd in self.cmds:
            print u'  {}'.format(cmd)
        print u'MEMORY: {}'.format(self.mem)


def parse_q(fn):
    res = Q()
    with codecs.open(fn, encoding='utf-8') as f:
        ln = 0
        for line in f.readlines():
            ln += 1
            line = line.strip()

            def err(desc):
                raise ValueError(u'error in question {} line {}: {}'.format(fn, ln, desc))

            if not line:
                continue

            if line.startswith('//'):
                print line
                continue

            if line in ALL_CMDS:
                res.cmds.add(line)
                continue

            m = re.match(u'mem\s+size\s+(\d+)$', line)
            if m:
                res.mem = [None] * int(m.group(1))
                continue

            m = re.match(u'mem\s*\[\s*(\d+)\s*\]\s*=\s*(\w+)$', line)
            if m:
                try:
                    val = int(m.group(2))
                    res.mem[int(m.group(1))] = val
                except ValueError:
                    val = m.group(2)
                    if len(val) > 1:
                        err('mem value too long')
                    res.mem[int(m.group(1))] = val
                continue

            err('unknown line')

    return res


class A:
    def __init__(self):
        self.insts = []
        self.labels = {}

    def dump(self):
        print u'LABELS (total {}):'.format(len(self.labels))
        for k, v in self.labels.iteritems():
            print u'  {}: pc {}'.format(k, v)
        print u'INSTS (total {}):'.format(len(self.insts))
        for pc, inst in enumerate(self.insts):
            print u'  pc {}: {}'.format(pc, inst)


def parse_a(q, fn):
    res = A()
    with codecs.open(fn, encoding='utf-8') as f:
        pc = 0
        ln = 0

        def err(desc):
            raise ValueError(u'error in program {} line {}: {}'.format(fn, ln, desc))

        for line in f.readlines():
            ln += 1
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            m = re.match(r'(\w+)\s*:$', line)
            if m:
                lbl = m.group(1)
                if lbl in res.labels.keys():
                    err(u'duplicate label {}'.format(lbl))
                res.labels[lbl] = pc
                continue

            # 0 args
            m = re.match(ur'(inbox|outbox)$', line)
            if m:
                cmd = m.group(1)
                if cmd not in q.cmds:
                    err(u'command not allowed on this level: {}'.format(cmd))
                res.insts.append((cmd,))
                pc += 1
                continue

            # 1 arg: label
            m = re.match(ur'(jump|jumpn|jumpz)\s+(\w+)$', line)
            if m:
                cmd, lbl = m.group(1), m.group(2)
                if cmd not in q.cmds:
                    err(u'command not allowed on this level: {}'.format(cmd))
                res.insts.append((cmd, lbl))
                pc += 1
                continue

            # 1 arg: addr
            m = re.match(ur'(copyfrom|copyto|add|sub)\s+(\d+)$', line)
            if m:
                cmd, addr = m.group(1), int(m.group(2))
                if cmd not in q.cmds:
                    err(u'command not allowed on this level: {}'.format(cmd))
                res.insts.append((cmd, 'addr', addr))
                pc += 1
                continue

            err(u'unknown instruction')

    return res


class Data:
    def __init__(self):
        self.boxes = []

    def dump(self):
        print u'DATA (total {})'.format(len(self.boxes))
        for box in self.boxes:
            print u'  {}'.format(box)


def parse_data(fn):
    res = Data()
    with codecs.open(fn, encoding='utf-8') as f:
        ln = 0

        def err(desc):
            raise ValueError(u'error in data {} line {}: {}'.format(fn, ln, desc))

        for line in f.readlines():
            ln += 1
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            try:
                val = int(line)
                res.boxes.append(val)
            except ValueError:
                if len(line) > 1:
                    err(u'string length more than 1: {}'.format(line))
                res.boxes.append(line)

    return res


def run(q, a, inn):
    # init
    pc = 0
    innpc = 0
    mem = q.mem[:]
    acc = None
    out = []

    def err(desc):
        raise ValueError(u'runtime error in pc {}: {}'.format(pc, desc))

    def reject_str(val, desc):
        if isinstance(val, basestring):
            err(desc)

    while True:
        if pc >= len(a.insts):
            print '* PROGRAM ENDED'
            break

        inst = a.insts[pc]
        cmd = inst[0]

        if cmd == 'inbox':
            if innpc >= len(inn.boxes):
                print '* NO MORE INPUT'
                break

            acc = inn.boxes[innpc]
            innpc += 1
            pc += 1
            continue

        if cmd == 'outbox':
            if acc is None:
                err(u'cannot outbox None at accumulator')
            out.append(acc)
            acc = None
            pc += 1
            continue

        if cmd == 'jump':
            lbl = inst[1]
            to_pc = a.labels.get(lbl)
            if to_pc is None:
                err(u'label {} is not known'.format(lbl))
            pc = to_pc
            continue

        if cmd == 'copyfrom':
            addr = inst[2]
            if mem[addr] is None:
                err(u'None is at mem addr {}'.format(addr))

            acc = mem[addr]
            pc += 1
            continue

        if cmd == 'copyto':
            addr = inst[2]
            if acc is None:
                err(u'cannot copy None to addr {}'.format(addr))

            mem[addr] = acc
            pc += 1
            continue

        if cmd == 'add':
            addr = inst[2]
            if mem[addr] is None:
                err(u'cannot add accumulator to None at addr {}'.format(addr))
            reject_str(mem[addr], u'addr {} contains a character'.format(addr))
            if acc is None:
                err(u'cannot add addr {} to None at accumulator'.format(addr))
            reject_str(acc, u'accumulator contains a character')

            acc = acc + mem[addr]
            pc += 1
            continue

        if cmd == 'jumpz':
            lbl = inst[1]
            to_pc = a.labels.get(lbl)
            if to_pc is None:
                err(u'label {} is not known'.format(lbl))
            if acc is None:
                err(u'cannot jumpz with None at accumulator')
            if acc == 0:
                pc = to_pc
            else:
                pc += 1
            continue

        if cmd == 'sub':
            addr = inst[2]
            if mem[addr] is None:
                err(u'cannot do accumulator sub None at addr {}'.format(addr))
            reject_str(mem[addr], u'addr {} contains a character'.format(addr))
            if acc is None:
                err(u'cannot do None at accumulator sub addr {}'.format(addr))
            reject_str(acc, u'accumulator contains a character')

            acc = acc - mem[addr]
            pc += 1
            continue

        err(u'unknown command: {}'.format(cmd))

    return out


def main():
    qdir = sys.argv[1]
    ans = sys.argv[2]

    q = parse_q(qdir + '/q.txt')
    q.dump()

    a = parse_a(q, ans)
    a.dump()

    infiles = glob.glob(qdir + '/*.in')
    for infile in infiles:
        outfile = infile[:-2] + 'out'
        if not os.path.isfile(infile) or not os.path.isfile(outfile):
            raise ValueError(u'Can not read {} or {}'.format(infile, outfile))

        inn = parse_data(infile)
        inn.dump()

        out_right = parse_data(outfile)
        out_boxes = run(q, a, inn)

        if out_boxes == out_right.boxes:
            print u'BETUUUUUUUUUUUULLLLLLLLLLL'
        else:
            print u'SALAHHHH, output mu {}, harusnya {}'.format(out_boxes, out_right.boxes)


main()
