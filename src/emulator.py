import sabre
import math

class Emulator:
    def __init__(self, movie, network):
        # setting globals in sabre
        sabre.verbose = False
        sabre.buffer_contents = []
        sabre.rebuffer_time = 0
        
        # load the movie and create the manifest
        manifest = sabre.load_json(movie)
        self.bitrates = manifest['bitrates_kbps']
        
        utility_offset = 0 - math.log(self.bitrates[0])
        utilities = [math.log(b) + utility_offset for b in self.bitrates] 
        sabre.manifest = sabre.ManifestInfo(segment_time = manifest['segment_duration_ms'], 
                                     bitrates     = self.bitrates,                                         
                                     utilities    = utilities, 
                                     segments     = manifest['segment_sizes_bits'])
        # load and save the network trace
        network_trace = sabre.load_json(network)
        network_trace = [sabre.NetworkPeriod(time = p['duration_ms'],                                  
                                       bandwidth = p['bandwidth_kbps'],     
                                       latency   = p['latency_ms'])                                   
                                       for p in network_trace] 
        sabre.network = sabre.NetworkModel(network_trace)

        self.current_segment = 0
        self.last_rebuff_time = 0
        
        def get_buffer_level():
            return sabre.get_buffer_level()
        def get_segs(n, m):
            return sabre.manifest.segments[n:m]
        def get_n_segs_left(self):
            return len(sabre.manifest.segments) - self.current_segment
        
        def step(self, quality):
            size = sabre.manifest.segments[self.current_segment][quality]
            download_metric = sabre.network.download(size, self.current_segment, quality, sabre.get_buffer_level(), 0)
            if self.current_segment > 0:
                sabre.deplete_buffer(download_metric.time)
            rebuff = sabre.rebuffer_time - self.last_rebuff_time
            sabre.buffer_contents.append(download_metric.quality)
            self.current_segment += 1

            download_time = download_metric.time - download_metric.time_to_first_bit                  
            throughput = download_metric.downloaded / download_time                                            
            latency    = download_metric.time_to_first_bit 

            return throughput, latency, rebuff
