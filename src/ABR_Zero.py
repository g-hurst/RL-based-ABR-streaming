import sabre

class ABR_Zero(sabre.Abr):
    # class method to overload that selects the next bitrate
    def get_quality_delay(self, segment_index:int) -> tuple:
        quality = 0
        delay = 0
        return (quality, delay)
