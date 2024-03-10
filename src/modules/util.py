def convert_resolution(width, height, ARR_width, ARR_height):
    original_aspect_ratio = width / height

    if ARR_width / ARR_height > original_aspect_ratio:
        # Horizontal aspect ratio
        new_width = int(height * (ARR_width / ARR_height))
        new_height = height
    else:
        # Vertical aspect ratio
        new_height = int(width * (ARR_height / ARR_width))
        new_width = width

    return new_width, new_height