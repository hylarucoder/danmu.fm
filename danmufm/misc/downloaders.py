# -*- coding: utf-8 -*-

"""
Module For Downloader-Related Tasks

Just Download With Pure Python
"""


import logging
import math
import os
import requests
import subprocess
import sys
import time



class Downloader(object):
    """
    Base downloader class.

    Every subclass should implement the _start_download method.

    Usage::

      >>> import downloaders
      >>> d = downloaders.SubclassFromDownloader()
      >>> d.download('http://example.com', 'save/to/this/file')
    """

    def _start_download(self, url, filename, resume):
        """
        Actual method to download the given url to the given file.
        This method should be implemented by the subclass.
        """
        raise NotImplementedError("Subclasses should implement this")

    def download(self, url, filename, resume=False):
        """
        Download the given url to the given file. When the download
        is aborted by the user, the partially downloaded file is also removed.
        """

        try:
            self._start_download(url, filename, resume)
        except KeyboardInterrupt as e:
            # keep the file if resume is True
            if not resume:
                logging.info('Keyboard Interrupt -- Removing partial file: %s',
                             filename)
                try:
                    os.remove(filename)
                except OSError:
                    pass
            raise e



def format_bytes(bytes):
    """
    Get human readable version of given bytes.
    Ripped from https://github.com/rg3/youtube-dl
    """
    if bytes is None:
        return 'N/A'
    if type(bytes) is str:
        bytes = float(bytes)
    if bytes == 0.0:
        exponent = 0
    else:
        exponent = int(math.log(bytes, 1024.0))
    suffix = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'][exponent]
    converted = float(bytes) / float(1024 ** exponent)
    return '{0:.2f}{1}'.format(converted, suffix)


class DownloadProgress(object):
    """
    Report download progress.
    Inspired by https://github.com/rg3/youtube-dl
    """

    def __init__(self, total):
        if total in [0, '0', None]:
            self._total = None
        else:
            self._total = int(total)

        self._current = 0
        self._start = 0
        self._now = 0

        self._finished = False

    def start(self):
        self._now = time.time()
        self._start = self._now

    def stop(self):
        self._now = time.time()
        self._finished = True
        self._total = self._current
        self.report_progress()

    def read(self, bytes):
        self._now = time.time()
        self._current += bytes
        self.report_progress()

    def report(self, bytes):
        self._now = time.time()
        self._current = bytes
        self.report_progress()

    def calc_percent(self):
        if self._total is None:
            return '--%'
        if self._total == 0:
            return '100% done'
        percentage = int(float(self._current) / float(self._total) * 100.0)
        done = int(percentage / 2)
        return '[{0: <50}] {1}%'.format(done * '#', percentage)

    def calc_speed(self):
        dif = self._now - self._start
        if self._current == 0 or dif < 0.001:  # One millisecond
            return '---b/s'
        return '{0}/s'.format(format_bytes(float(self._current) / dif))

    def report_progress(self):
        """Report download progress."""
        percent = self.calc_percent()
        total = format_bytes(self._total)

        speed = self.calc_speed()
        total_speed_report = '{0} at {1}'.format(total, speed)

        report = '\r{0: <56} {1: >30}'.format(percent, total_speed_report)

        if self._finished:
            print(report)
        else:
            print(report, end="")
        sys.stdout.flush()


class NativeDownloader(Downloader):
    """
    'Native' python downloader -- slower than the external downloaders.

    :param session: Requests session.
    """

    def __init__(self, session):
        self.session = session

    def _start_download(self, url, filename, resume=False):
        # resume has no meaning if the file doesn't exists!
        resume = resume and os.path.exists(filename)

        headers = {}
        filesize = None
        if resume:
            filesize = os.path.getsize(filename)
            headers['Range'] = 'bytes={}-'.format(filesize)
            logging.info('Resume downloading %s -> %s', url, filename)
        else:
            logging.info('Downloading %s -> %s', url, filename)

        attempts_count = 0
        error_msg = ''
        while attempts_count < 5:
            r = self.session.get(url, stream=True, headers=headers)

            if r.status_code != 200:
                # because in resume state we are downloading only a
                # portion of requested file, server may return
                # following HTTP codes:
                # 206: Partial Content
                # 416: Requested Range Not Satisfiable
                # which are OK for us.
                if resume and r.status_code == 206:
                    pass
                elif resume and r.status_code == 416:
                    logging.info('%s already downloaded', filename)
                    r.close()
                    return True
                else:
                    print(r.status_code)
                    print(url)
                    print(filesize)
                    logging.warn('Probably the file is missing from the AWS '
                                 'repository...  waiting.')

                    if r.reason:
                        error_msg = r.reason + ' ' + str(r.status_code)
                    else:
                        error_msg = 'HTTP Error ' + str(r.status_code)

                    wait_interval = 2 ** (attempts_count + 1)
                    msg = 'Error downloading, will retry in {0} seconds ...'
                    print(msg.format(wait_interval))
                    time.sleep(wait_interval)
                    attempts_count += 1
                    continue

            if resume and r.status_code == 200:
                # if the server returns HTTP code 200 while we are in
                # resume mode, it means that the server does not support
                # partial downloads.
                resume = False

            content_length = r.headers.get('content-length')
            chunk_sz = 1048576
            progress = DownloadProgress(content_length)
            progress.start()
            f = open(filename, 'ab') if resume else open(filename, 'wb')
            while True:
                data = r.raw.read(chunk_sz, decode_content=True)
                if not data:
                    progress.stop()
                    break
                progress.report(r.raw.tell())
                f.write(data)
            f.close()
            r.close()
            return True

        if attempts_count == 5:
            logging.warn('Skipping, can\'t download file ...')
            logging.error(error_msg)
            return False


def get_downloader(session, class_name, args):
    """
    Decides which downloader to use.
    """

    external = {
        'curl': CurlDownloader,
    }

    for bin, class_ in external.iteritems():
        if getattr(args, bin):
            return class_(session, bin=getattr(args, bin))

    return NativeDownloader(session)
