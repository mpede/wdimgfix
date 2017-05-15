
import os
import re
import binascii
import click
import d7000    # preview at 114,306; subIDF at 468,472
#        (position preview) + 20 + (4 - (position preview mod 4) or 0 if %4=0)


@click.command()
@click.option('--fix', is_flag=True)
@click.option('--jpgonly', is_flag=True)
@click.option('--nefonly', is_flag=True)
def cli(fix, jpgonly, nefonly):
    """\b
Fix for JPGS & D7000/D60 NEFs corrupted by a WD disk failure
by C. Schmidt chris@2309.net
This script will restore file headers when the first 512 bytes got wiped.
    """

    def fix_image(filename, filetype):

        def nikonD7000(bts, filename):
            previewpos = bts.find(b'\xff\xd9\x00')
            if previewpos % 4 == 0:
                previewdiff = 0
            else:
                previewdiff = 4 - (previewpos % 4)
            previewposhex = binascii.a2b_hex('{:08x}'
                                             .format(previewpos +
                                                     20 + previewdiff))
            subidfpos = bts.find(b'\x00\x08\x00\xfe')
            subidfstarthex = binascii.a2b_hex('{:08x}'.format(subidfpos))
            subidfendhex = binascii.a2b_hex('{:08x}'.format(subidfpos+120))
            with open(filename, 'r+b') as f:
                f.seek(0)
                f.write(d7000.header)
                f.seek(114)
                f.write(previewposhex)
                f.seek(306)
                f.write(previewposhex)
                f.seek(468)
                f.write(subidfstarthex+subidfendhex)

        def nikonD60(bts, filename):
            print('skipping... not ', end='')

        findD7000 = b'ASCII\x00\x00\x00\x20\x20'
        findD60 = b'ASCII\x00\x00\x00CS1\x20\x20'

        with open(filename, 'rb') as f:
            bts = f.read(196560)

        if bts[:4] == b'\xF5\x01\x00\x00':

            if fix:

                if filetype == 'jpg':
                    with open(filename, 'r+b') as f:
                        f.seek(0)
                        f.write(b'\xff\xd8\xff\xe1\xff\xfe')
                    print("fixed: {0}".format(filename))

                elif filetype == 'nef':
                    if bts.find(findD7000) != -1:
                        nikonD7000(bts, filename)
                    elif bts.find(findD60) != -1:
                        nikonD60(bts, filename)

                    print("fixed: {0}".format(filename), flush=True)

            else:
                # if bts.find(findD7000) != -1 and filetype != 'jpg':
                #     print('D7000  - ', end='')
                # elif bts.find(findD60) != -1 and filetype != 'jpg':
                #     print('D60    - ', end='')
                # else:
                #     print('JPG    - ', end='')
                print("{0:17} ==> {1:14} {2}"
                      .format(filename, 'corrupted', ' '
                              .join(["%02X" % x for x in bts[:20]])), flush=True)

        else:
            if not fix:
                # if bts.find(findD7000) != -1 and filetype != 'jpg':
                #     print('D7000  - ', end='')
                # elif bts.find(findD60) != -1 and filetype != 'jpg':
                #     print('D60    - ', end='')
                # else:
                #     print('JPG    - ', end='')
                print("{0:17} ==> {1:14} {2}"
                      .format(filename, 'fine', ' '
                              .join(["%02X" % x for x in bts[:20]])), flush=True)

    click.echo('\nFinding and fixing images...\n')

    foundfiles = []
    filecount = 0
    fheaders = []

    for path, dirs, files in os.walk('.'):
        for name in files:
            if re.search('\.(jpg|nef|jpeg)$', name, re.I):
                filename = os.path.join(path, name)
                if re.search('\.(jpg|jpeg)', name, re.I):
                    filetype = 'jpg'
                    if not nefonly:
                        fix_image(filename, filetype)
                else:
                    filetype = 'nef'
                    if not jpgonly:
                        fix_image(filename, filetype)
