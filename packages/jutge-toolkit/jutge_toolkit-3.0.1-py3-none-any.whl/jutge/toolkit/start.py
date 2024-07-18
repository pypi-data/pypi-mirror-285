#!/usr/bin/env python3
# coding=utf-8

"""
This script is used to start correcting a submission.
"""

import argparse
import logging
import os
import resource
import sys

from jutge import util


def main():
    """main"""

    util.init_logging()

    parser = argparse.ArgumentParser(
        description='Correct a submission')
    parser.add_argument('name')
    parser.add_argument(
        '--no-wrapping',
        action='store_true',
        help='do not wrap')
    args = parser.parse_args()

    wrapping = not args.no_wrapping

    logging.info('name: %s' % args.name)
    logging.info('wrapping: %s' % str(wrapping))

    if wrapping:
        logging.info('starting correction')
        logging.info('cwd=%s' % os.getcwd())
        logging.info('user=%s' % util.get_username())
        logging.info('host=%s' % util.get_hostname())

        logging.info('setting ulimits')
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
        resource.setrlimit(resource.RLIMIT_NPROC, (1000, 1000))

        logging.info('setting umask')
        os.umask(0o077)

        logging.info('decompressing submission')
        util.del_dir('submission')
        util.mkdir('submission')
        util.extract_tgz('submission.tgz', 'submission')

        logging.info('decompressing problem')
        util.del_dir('problem')
        util.mkdir('problem')
        util.extract_tgz('problem.tgz', 'problem')

        logging.info('decompressing driver')
        util.del_dir('driver')
        util.mkdir('driver')
        util.extract_tgz('driver.tgz', 'driver')

        logging.info('mkdir solution')
        util.del_dir('solution')
        util.mkdir('solution')

        logging.info('mkdir correction')
        util.del_dir('correction')
        util.mkdir('correction')

    # http://stackoverflow.com/questions/692000/how-do-i-write-stderr-to-a-file-while-using-tee-with-a-pipe

    cmd = 'bash -c "python3 driver/judge.py %s </dev/null > >(tee stdout.txt) 2> >(tee stderr.txt >&2)"' % args.name
    logging.info('executing %s' % cmd)
    os.system(cmd)
    os.rename("stderr.txt", "correction/stderr.txt")
    os.rename("stdout.txt", "correction/stdout.txt")
    os.system("chmod -R u+rwX,go-rwx .")

    logging.info('end of correction')

    if wrapping:
        logging.info('compressing correction')
        util.create_tgz('correction.tgz', '.', 'correction')

    logging.info('flushing and closing files')
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdout.close()
    sys.stderr.close()
    sys.stdin.close()
    # noinspection PyProtectedMember
    os._exit(0)


if __name__ == '__main__':
    main()
