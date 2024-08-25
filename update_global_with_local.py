# This is the GLOBAL data that is in the GLOBAL grid
# It needs to have parts of it updated with the local data from the camera
global_data = [
    {'color': [240, 59, 32, 180], 'height': [10], 'id': 0, 'interactive': True, 'name': 'Office'},
    {'color': [0, 0, 0, 0], 'height': [1], 'id': 1, 'interactive': True, 'name': 'None'},
    {'color': [240, 59, 32, 180], 'height': [10], 'id': 2, 'interactive': True, 'name': 'Office'},
    {'color': [0, 0, 0, 0], 'height': [1], 'id': 3, 'interactive': True, 'name': 'None'},
    {'color': [0, 0, 0, 0], 'height': [1], 'id': 4, 'interactive': True, 'name': 'None'},
    {'color': [0, 0, 0, 0], 'height': [1], 'id': 5, 'interactive': True, 'name': 'None'},
    {'color': [240, 59, 32, 180], 'height': [10], 'id': 6, 'interactive': True, 'name': 'Office'},
    {'color': [0, 0, 0, 0], 'height': [1], 'id': 7, 'interactive': True, 'name': 'None'},
    {'color': [240, 59, 32, 180], 'height': [10], 'id': 8, 'interactive': True, 'name': 'Office'}
    ]

# We have this information from create_smaller_grid and the list generated after that.
# This is the list of ids to change in the larger grid (json_str)
list_ids_to_change = [0,1,2]

def update_global(mapped_data, global_data, global_ids_to_change):
    """Mapped data is the local information that needs to be updated to the global data."""
    # We should go through each item from the local mapped_data.
    for updated_info in mapped_data:
        # We are looking at one specific cell now. We need to update the json_str at each ID in list_ids_to_change
        # So, we need to find the ID to change, in the original json_str
        for item in global_data: #json_str is a LIST, each item is a DICT
            for global_id in global_ids_to_change:
                # Comparing the original ids -- item['id'] -- against the list of ids to change
                if item['id'] < global_id:
                    break # if we are at item['id'] of 0, and the first id_to_change is 2, 0 won't be in the list.
                    # want to move onto the next item in the json_str

                elif item['id'] == global_id:
                    #print("Original info:",item)
                    # Now we want to update this info based on the information from mapping_markers
                    #print("---------------")
                    item['color'] = updated_info['color']
                    item['height'] = updated_info['height']
                    item['interactive'] = updated_info['interactive']
                    item['name'] = updated_info['name']
                    # print("---------------")

# print("Original:",global_data)
# with open('mapped_data/mapped_file_0.json', 'r') as f1:
#     mapped_data = json.load(f1)
# update_global(mapped_data, global_data, list_ids_to_change)
# print("Changed:",global_data)
