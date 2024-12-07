import sabre
import math

class Emulator:
    def __init__(self, movie, network, max_buffer=25):
        self.movie   = movie
        self.network = network
        self.max_buffer = max_buffer
        self.setup(movie, network, max_buffer)

    def setup(self, movie, network, max_buffer=25):
        sabre.verbose = False
        sabre.buffer_contents = []
        sabre.rebuffer_time = 0
        sabre.rebuffer_event_count = 0
        sabre.pending_quality_up = []
        sabre.reaction_metrics = []
        sabre.buffer_fcc = 0
        sabre.played_utility = 0
        sabre.played_bitrate = 0
        sabre.total_play_time = 0
        sabre.total_bitrate_change = 0
        sabre.total_log_bitrate_change = 0
        sabre.total_reaction_time = 0
        sabre.last_played = None
        sabre.max_buffer_size = 1000 * max_buffer
        sabre.rampup_threshold = None
        sabre.overestimate_count = 0
        sabre.overestimate_average = 0
        sabre.goodestimate_count = 0
        sabre.goodestimate_average = 0
        sabre.estimate_average = 0
        sabre.rampup_origin = 0
        sabre.rampup_time = None
        
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

    def reset(self):
        self.setup(self.movie, self.network, self.max_buffer)

    def get_buffer_level(self):
        return sabre.get_buffer_level()

    def get_segs(self, n, m):
        return sabre.manifest.segments[n:m]

    def get_n_segs_left(self):
        return len(sabre.manifest.segments) - self.current_segment
    
    def step(self, quality):
        size = sabre.manifest.segments[self.current_segment][quality]
        download_metric = sabre.network.download(size, self.current_segment, quality, sabre.get_buffer_level(), 0)
        if self.current_segment > 0:
            sabre.deplete_buffer(download_metric.time)
        rebuff = sabre.rebuffer_time - self.last_rebuff_time
        self.last_rebuff_time = sabre.rebuffer_time
        sabre.buffer_contents.append(download_metric.quality)
        self.current_segment += 1

        download_time = download_metric.time - download_metric.time_to_first_bit                  
        throughput = download_metric.downloaded / download_time                                            
        latency    = download_metric.time_to_first_bit 

        return throughput, latency, rebuff
