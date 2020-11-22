from utils import mkdir
from utils.reader import Reader


class MView(Reader):
    def __init__(self, filename):
        with open(filename, 'rb') as fh:
            super().__init__(fh.read(), 'little')

        self.filename = filename

    def parse(self):
        folder = self.filename.split('.')[0]
        mkdir(folder)

        while self.tell() < len(self.buffer):
            name = self.readString()
            file_type = self.readString()

            is_compressed = self.readUInt32()
            compressed_length = self.readUInt32()
            decompressed_length = self.readUInt32()

            data = self.read(compressed_length)

            if is_compressed & 1:
                data = self.decompress(data, decompressed_length)

            output = open('%s/%s' % (folder, name), 'wb')
            output.write(data)
            output.close()

            print(name, file_type)

        print('COMPLETED!!!')

    @staticmethod
    def decompress(a, b):
        c = bytearray(b)
        d = 0
        e = [0] * 4096
        f = [0] * 4096
        g = 256
        h = len(a)
        k = 0
        l = 1
        m = 0
        n = 1

        c[d] = a[0]
        d += 1

        r = 1
        while True:
            n = r + (r >> 1)
            if (n + 1) >= h:
                break
            m = a[n + 1]
            n = a[n]
            p = (m << 4 | n >> 4) if r & 1 else ((m & 15) << 8 | n)
            if p < g:
                if 256 > p:
                    m = d
                    n = 1
                    c[d] = p
                    d += 1
                else:
                    m = d
                    n = f[p]
                    p = e[p]
                    q = p + n
                    while p < q:
                        c[d] = c[p]
                        d += 1
                        p += 1
            elif p == g:
                m = d
                n = l + 1
                p = k
                q = k + l
                while p < q:
                    c[d] = c[p]
                    d += 1
                    p += 1
                c[d] = c[k]
                d += 1
            else:
                break

            e[g] = k
            f[g] = l + 1
            g += 1
            k = m
            l = n
            g = 256 if 4096 <= g else g
            r += 1

        return c if d == b else None


if __name__ == '__main__':
    mview = MView('x6k7oilwxr.mview')
    mview.parse()
