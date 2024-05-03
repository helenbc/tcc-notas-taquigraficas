import json
import os
import csv

def read_json_as_dict(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

compressed_prompts_folder = "../compressed_prompts_v3/"
model_responses_folder = "../responses_v3/"

def load_all_json_files_in_folder(folder):
    all_files = os.listdir(folder)

    def is_valid_json_file(f):
        invalid_terms = ['ignored', 'processing', 'error']
        return f.endswith('.json') and not any(term in f for term in invalid_terms)

    json_files = [f for f in all_files if is_valid_json_file(f)]
    return [read_json_as_dict(folder + f) for f in json_files]

compressed_prompts = load_all_json_files_in_folder(compressed_prompts_folder)
model_responses = load_all_json_files_in_folder(model_responses_folder)

def calculate_total_elapsed_time_and_mean(dicts, key = 'elapsed_time'):
    total_elapsed_time = 0
    for d in dicts:
        elapsed_time = d.get(key, None)
        if elapsed_time is None:
            print(d)
            raise ValueError("elapsed_time not found in dict")

        total_elapsed_time += elapsed_time
    return total_elapsed_time, total_elapsed_time / len(dicts)

total_elapsed_time, mean_elapsed_time = calculate_total_elapsed_time_and_mean(compressed_prompts)
total_in_hours = total_elapsed_time / 3600
mean_in_hours = mean_elapsed_time / 3600

with open('elapsed_times.csv', mode='w') as f:
    writer = csv.writer(f)
    writer.writerow(['type', 'total_elapsed_time', 'mean_elapsed_time', 'total_elapsed_time_in_hours', 'mean_elapsed_time_in_hours'])
    writer.writerow(['compressed_prompts', total_elapsed_time, mean_elapsed_time, total_in_hours, mean_in_hours])

total_elapsed_time, mean_elapsed_time = calculate_total_elapsed_time_and_mean(model_responses, key="response_elapsed_time")
total_in_hours = total_elapsed_time / 3600
mean_in_hours = mean_elapsed_time / 3600

with open('elapsed_times.csv', mode='a') as f:
    writer = csv.writer(f)
    writer.writerow(['model_responses', total_elapsed_time, mean_elapsed_time, total_in_hours, mean_in_hours])
    