import os
import sys
import json
import yaml
import shutil

def extract_data_from_json(json_file):
    try:
        # print(json_file)
        f = open(json_file, 'r', encoding='utf-8')
        data = json.load(f)
        f.close()
        return data
    except FileNotFoundError:
        print("Requested file does not exist")
        return None

def extract_json_attribute_data(json_file, attribute):
    attribute_data = extract_data_from_json(json_file)[attribute]
    return attribute_data

def extract_json_keys(json_file):
    keys = extract_data_from_json(json_file).keys()
    return keys

def export_dictionary_to_json(dictionary, output):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, output + ".json"), 'w', encoding='utf-8') as outfile:
        json.dump(dictionary, outfile)

def remove_dir_at_path(dir_path):
    if os.path.exists(dir_path):
        # os.rmdir(dir_path)
        shutil.rmtree(dir_path.encode('unicode_escape'))
        return True
    return False

def create_dir_at_path(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        return True
    return False

def output_error_to_stderr(error):
    sys.stderr.write(error)
    sys.stderr.flush()

def yaml_load(file_path):
    data = None
    
    with open(file_path, 'r', encoding='utf-8') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    stream.close()
    return data

def yaml_dump(data, file_path):
    mode = 'x'

    if os.path.isfile(file_path):
        mode = 'w'

    with open(file_path, mode, encoding='utf-8') as f:
        try:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as exc:
            print(exc)
            return False
    
    f.close()

    return True

def file_exists(file_path):
    if os.path.isfile(file_path):
        return True
    return False