def parse_key_value_string(data):
    result = {}
    lines = data.strip().split('\n')
    for line in lines:
        key, value = parse_key_value_line(line)
        result[key] = value
    return result


def parse_key_value_file(filename):
    result = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Ignore empty lines
                key, value = parse_key_value_line(line)
                result[key] = value
    return result


def parse_key_value_line(line):
    key, value = line.split('=')
    return key.strip(), value.strip()
