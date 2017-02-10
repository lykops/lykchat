import subprocess
import sys , os
from library.config.wechat import os_type


def print_qr(filedir, enablecmdqr=True):
        try:
            b = u'\u2588'
            sys.stdout.write(b + '\r')
            sys.stdout.flush()
        except UnicodeEncodeError:
            BLOCK = 'MM'
        else:
            BLOCK = b
            
        white = BLOCK
        black = '  '
        size = 37
        padding = 3
        
        try:
            from PIL import Image
            img = Image.open(filedir)
            times = img.size[0] / (size + padding * 2)
            rgb = img.convert('RGB')
            try:
                    blockCount = int(enablecmdqr)
                    assert(0 < abs(blockCount))
            except:
                    blockCount = 1
            finally:
                    white *= abs(blockCount)
                    if blockCount < 0: white, black = black, white
            sys.stdout.write(' ' * 50 + '\r')
            sys.stdout.flush()
            qr = white * (size + 2) + '\n'
            startPoint = padding + 0.5
            for y in range(size):
                qr += white
                for x in range(size):
                    r, g, b = rgb.getpixel(((x + startPoint) * times, (y + startPoint) * times))
                    qr += white if r > 127 else black
                qr += white + '\n'
            qr += white * (size + 2) + '\n'
            sys.stdout.write(qr)
        except ImportError:
            print('pillow should be installed to use command line qrCode: pip install pillow')
            if os_type == 'Darwin':
                subprocess.call(['open', filedir])
            elif os_type == 'Linux':
                subprocess.call(['xdg-open', filedir])
            else:
                os.startfile(filedir)
