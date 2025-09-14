def process(image_file):
    image_path = f'temp_{image_file.filename}'
    image_file.save(image_path)

    soil_info = "Loamy soil detected with good drainage properties."

    import os
    os.remove(image_path)

    return soil_info
