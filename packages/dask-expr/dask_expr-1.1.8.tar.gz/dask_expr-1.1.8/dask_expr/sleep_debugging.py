import coiled

# @coiled.function(name="test")
def sleep_for_20_minutes(i):
    import time
    time.sleep(60 * 20)
    return i