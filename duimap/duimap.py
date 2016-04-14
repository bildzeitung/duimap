#!/usr/bin/env python
"""
 du for IMAP

 Author: bildzeitung@gmail.com
"""

import argparse
import imaplib


def printdu(servername, user, password_file):
    pwd = open(password_file).read().strip()
    server = imaplib.IMAP4_SSL(servername)
    # server.debug = 10
    server.login(user, pwd)

    rc, mboxes = server.list()
    if rc != 'OK':
        print 'Could not retrieve list of mailboxes'
        exit(1)

    grand_total = 0
    mboxes = [x.split()[2] for x in mboxes]
    for mbox in sorted(mboxes):
        rc, msgs = server.select(mbox, readonly=True)

        if rc == 'NO':  # skip ones that fail EXAMINE
            continue

        rc, items = server.uid('search', None, 'ALL')
        if rc != 'OK':
            continue

        items = items[0].split()
        if not items:
            continue

        rc, sizes = server.uid('fetch', '%s:%s' % (items[0], items[-1]), '(UID RFC822.SIZE)')
        if rc != 'OK':
            print 'ERROR getting sizes', rc, sizes
            continue

        total = sum(int(x.split()[0]) for x in sizes)
        print '%10d %s' % (total, mbox[1:-1])
        grand_total += total

    print '%10d .' % grand_total


def main():
    argp = argparse.ArgumentParser(description='Display IMAP folder usage')
    argp.add_argument('server', help='IMAP server and port')
    argp.add_argument('user', help='Username')
    argp.add_argument('password', help='File containing password')

    args = argp.parse_args()

    printdu(args.server, args.user, args.password)
