# Collect functions and settings for the MassBank workflow here, that may need to be adjusted over time.

def skip_compounds_mbank():
    """
    These compounds will be skipped and not exported.
    """
    mbank_skip_comp = ['Bezafibrate-d4','Olmesartan-d6','Iopromide-d3']
    return mbank_skip_comp
