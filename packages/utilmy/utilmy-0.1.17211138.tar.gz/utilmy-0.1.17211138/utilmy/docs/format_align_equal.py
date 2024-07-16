
import re

def align_equals(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    pattern = re.compile(r'^(\s*)(\S+)(\s*=\s*)(.*)')
    blocks = []
    current_block = []

    # Group lines into blocks of consecutive lines containing '='
    for line in lines:
        if pattern.match(line):
            current_block.append(line)
        else:
            if current_block:
                blocks.append(current_block)
                current_block = []
            blocks.append([line])
    if current_block:
        blocks.append(current_block)

    # Process each block to align '='
    aligned_lines = []
    for block in blocks:
        if len(block) > 1 and '=' in block[0]:
            max_equal_pos = 0
            parsed_lines = []
            # Determine the maximum '=' position in the current block
            for line in block:
                match = pattern.match(line)
                if match:
                    initial_whitespace, variable_part, equals_part, rest = match.groups()
                    equal_pos = len(initial_whitespace) + len(variable_part) + len(equals_part) - 1
                    max_equal_pos = max(max_equal_pos, equal_pos)
                    parsed_lines.append((initial_whitespace, variable_part, equals_part, rest, equal_pos))
            
            # Align '=' in the current block
            for parsed_line in parsed_lines:
                initial_whitespace, variable_part, equals_part, rest, current_equal_pos = parsed_line
                spaces_to_add = max_equal_pos - current_equal_pos
                aligned_line = f"{initial_whitespace}{variable_part} {' ' * spaces_to_add}= {rest}"
                aligned_lines.append(aligned_line)
        else:
            aligned_lines.extend(block)

    # Write the aligned content back to the file
    with open(filename, 'w') as file:
        file.writelines(aligned_lines)
