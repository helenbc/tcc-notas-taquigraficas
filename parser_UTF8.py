import os
import json

path = './small_responses_v2/'

def get_all_json_files(path):
    return [f for f in os.listdir(path) if f.endswith('.json')]


def transform_json_content_to_UTF8(json_file):
    with open(path + json_file, 'r') as f:
        content = f.read()
    return content

for json_file in get_all_json_files(path):
    content = transform_json_content_to_UTF8(json_file)
    new_content = json.loads(content)
    #overwrite the file with the new content with UTF-8
    with open(path + json_file, 'w', encoding='utf-8') as f:
        json.dump(new_content, f, ensure_ascii=False)