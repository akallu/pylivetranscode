import sys
import os
import time
import msvcrt

#non-standard modules
import livestreamer


class StreamGrabber(object):

    def __init__(self, stream_url, stream_read_size=8192, debug=False):
        self.stream_url = stream_url
        self.stream_read_size = stream_read_size
        self.debug = debug

        self.streams = livestreamer.streams(stream_url)
        self.active_stream_name = None
        self.active_stream_fd = None
        if not self.get_stream_names():
            raise ValueError('There are currently no streams being served by the URL, %s !' % (self.stream_url))
        self.set_active_stream('source' if 'source' in self.get_stream_names() else self.get_stream_names()[0])

    def get_stream_names(self):
        return self.streams.keys()

    def set_active_stream(self, stream_name):
        # close the stream fd if there was already an active stream set
        if self.active_stream_name is not None:
            self.active_stream_fd.close()
        if stream_name not in self.streams:
            raise ValueError('The specified stream_name, %s, is not present in the possible streams.' % (stream_name))
        self.active_stream_name = stream_name
        self.active_stream_fd = self.streams[stream_name].open()

    def get_stream_chunks(self):
        chunks_read = 0
        while True:
            if self.debug:
                print 'Chunks read : %s' % (chunks_read+1)
            yield self.active_stream_fd.read(self.stream_read_size)
            chunks_read += 1

def make_windows_fd_binary(fd):
    msvcrt.setmode(fd.fileno(), os.O_BINARY)

def main():
    TIME_LIMIT = 10
    is_windows = True
    urls = ('https://www.twitch.tv/odpixel', 'https://www.twitch.tv/wagamamatv')
    outfilename = os.path.join(os.getcwd(), 'source.out')

    with open(outfilename, 'w') as outfile:
        make_windows_fd_binary(outfile)
        for url in urls:
            sg = StreamGrabber(url)
            start_time = int(time.time())
            for stream_chunk in sg.get_stream_chunks():
                outfile.write(stream_chunk)
                current_time = int(time.time())
                if current_time - start_time > TIME_LIMIT:
                    break




if __name__ == "__main__":
    main()