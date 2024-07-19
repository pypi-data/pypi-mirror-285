#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Append cardiovascular data from a second file to a first file and optionally write the combined data to a new file.
In some cases, due to issue with the finometer during data collection, a single participant may end up with two seperate folders with seperate `.txt` files. 
This module provides a function to append the cardiovascular data from a 'part 2' file to a 'part 1' file. 
The combined data is returned as a list of strings. 
Optionally, the function can write the combined data to an output file. 

Notes
-----
 - This function is intended for use in the data cleaning process, but it should be used cautiously and documented appropriately in the research notes and final report appendices.
 - The function is *not* intended to be used to combine data from two seperate participants.


Example
-------
combined_data = merge_split_data('/path/to/part1_file.txt', '/path/to/part2_file.txt', part2_start_line=9, output_file='/path/to/output_file.txt')

'''


from ..dependencies import pl, Union, Optional, List

def merge_split_data(
    part1_file: Union[str, pl.Path],
    part2_file: Union[str, pl.Path],
    part2_start_line: str = 9, 
    output_file: Optional[Union[str, pl.Path]] = None
) -> List[str]:
    '''
    Appends cardiovascular data from part 2 file to part 1 file and optionally writes the combined data to an output file.

    Parameters
    ----------
    part1_file : Union[str, Path]
        File path of the part 1 file.
    part2_file : Union[str, Path]
        File path of the part 2 file.
    part2_start_line : int, optional
        The line number in the part 2 file from which to start appending the data (default is 9).
        Use this parameter to skip lines in the part 2 file, for example, to account for recalibration.
    output_file : Union[str, Path], optional
        File path of the output file to write the combined data (default is None).

    Returns
    -------
    List[str]
        List of combined cardiovascular data.
    '''
    
    # Step 1: Read in the part 1 file
    with open(part1_file, 'r') as f:
        lines_part1 = f.readlines()

    # Step 2: Save the header above line 9 in file 1
    header_part1 = lines_part1[:8]

    # Step 3: Save the data from line 9 down from file 1
    data_part1 = lines_part1[8:]

    # Step 4: Save the data from line 9 down in file 2
    with open(part2_file, 'r') as f:
        lines_part2 = f.readlines()[part2_start_line:]

    # Step 5: Append the data from file 2 to the bottom of the data from file 1
    combined_data = data_part1 + lines_part2
    
    if output_file is not None:
        # Step 6: Write all three things to a .txt file
        with open(output_file, 'w') as f:
            f.writelines(header_part1)
            f.writelines(combined_data)
    
    return combined_data