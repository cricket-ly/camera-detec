import asyncio
from test1 import function_a
from test2 import function_b
from test3 import function_c
from aruco_id_detector import calibrate

async def main(initial, local_rows, local_columns, grid_position_dict):
    # Run all the files together
    await asyncio.gather(function_b(), function_c(initial, local_rows, local_columns),function_a(grid_position_dict))

if __name__ == "__main__":
    # Initialization
    desired_aruco_dictionary = "DICT_4X4_50"
    # initial = int(input("Top left corner of LOCAL grid: "))
    # local_rows = int(input("Rows for LOCAL grid: "))
    # local_columns = int(input("Columns for LOCAL grid: "))
    initial = 0
    local_rows = 3
    local_columns = 3
    grid_position_dict = calibrate(desired_aruco_dictionary, local_rows, local_columns)
    asyncio.run(main(initial, local_rows, local_columns, grid_position_dict))
