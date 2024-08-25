import json

def mapping_markers_to_data(data_file):
    """This processes the data_file (JSON) of markers detected and returns a JSON file of
    info about them (color, height, ID, interactive, name)"""
    # # Load JSON Files
    # file_to_map = 'file_0'
    # with open(f'raw_data/{file_to_map}.json', 'r') as f1, open('aruco_codes.json', 'r') as f2:
    #     data_file = json.load(f1) # These are the markers detected by the camera
    #     codes_file = json.load(f2) # This is the 'key' mapping aruco codes to info about them

    with open('aruco_codes.json', 'r') as f2:
        codes_file = json.load(f2) # This is the 'key' mapping aruco codes to info about them

    # Extract the aruco ids from JSON file #1
    data = data_file.get('Data', [])
    #print(f"Data: {data}")
    markers = data['Marker ID'] # list of IDs
    #print('Markers:',markers)
    #print('------------')

    codes = codes_file.get('Codes', {})
    #print(f"Codes: {codes}")

    # Map aruco_ids to corresponding codes
    mapped_data = []
    index = 0

    # Go through each detected aruco marker, "item"
    for each_id in markers: # This is the one we want to check against in the 'keys'
        if each_id == 'None':
            #print(f"Aruco ID is {each_id} (NONE FOUND)")
            mapped_entry = {
                'color': [0, 0, 0, 0],
                'height': [1],
                'id': index,
                'interactive': True,
                'name': 'None'
                }
            mapped_data.append(mapped_entry)
        for key, value in codes.items():
            if value['aruco_id'] == each_id:
                #print(f"Aruco ID {each_id} is '{key}': {value}")
                name = key
                color = value['color']

                mapped_entry = {
                'color': color,
                'height': value['height'],
                'id': index,
                'interactive': True,
                'name': name
                }

                mapped_data.append(mapped_entry)
                break
        index += 1
        #input("Enter")

    return(mapped_data)
