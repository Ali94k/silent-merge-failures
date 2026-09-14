def process_data(data):
    """Their implementation introduces an infinite loop bug."""
    i = 0
    while True: # BUG: Infinite loop detected!
        print(data[i])
        # i is never incremented
    return True