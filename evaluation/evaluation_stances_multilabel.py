import json
import csv
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

global_y_pred = []
global_y_true = []

def read_and_split_csv(filename):
    # Criar listas para cada categoria de tamanho
    small_sessions = []
    medium_sessions = []
    big_sessions = []

    # Abrir o arquivo CSV
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Ler o id_session e session_size do arquivo CSV
            session_id = row['id_session']
            session_size = row['session_size']
            
            # Separar os IDs nas listas apropriadas
            if session_size == 'small':
                small_sessions.append(session_id)
            elif session_size == 'medium':
                medium_sessions.append(session_id)
            elif session_size == 'big':
                big_sessions.append(session_id)
            else:
                print(f"Session size '{session_size}' not recognized.")

    # Retorna as três listas
    return small_sessions, medium_sessions, big_sessions

# Exemplo de uso da função
small, medium, big = read_and_split_csv('./session_sizes.csv')
small_uncompressed = small[:]


def read_json_file_to_dict(path):
    with open(path, 'r') as f:
        content = f.read()
        dict = json.loads(content)
    return dict

def get_model_response_evaluation_mapping(dict, key1, key2):
    model_response_evaluation = dict[key1][key2]
    return model_response_evaluation


def get_label_for_stance(stance):
    if stance == 'FOR':
        return 0
    elif stance == 'NEUTRAL':
        return 1
    elif stance == 'AGAINST':
        return 2
    else:
        raise ValueError(f"Stance '{stance}' not recognized.")

def get_normalized_name(name):
    return name.replace('PRESIDENTE ', '').replace('PRESIDENTA ', '')

def calculate_metrics_for_sessions(session_ids, is_uncompressed=False):
    session_metrics = []

    ground_truths = []
    for session_id in session_ids:
        current = read_json_file_to_dict(f'./ground_truth/{session_id}_ground_truth.json')
        ground_truths.append(current)

    model_responses = []
    for session_id in session_ids:
        folder = '../responses_v3/'
        if is_uncompressed:
            folder = '../small_responses_v2/'

        current = read_json_file_to_dict(f'{folder}{session_id}.json')
        model_responses.append(current)

    for i in range(len(session_ids)):
        ground_truth = ground_truths[i]
        model_response = model_responses[i]

        key = 'model_response_evaluation'
        if is_uncompressed:
            key = 'model_response_evaluation_without_compression'

        mappings = get_model_response_evaluation_mapping(ground_truth, key, 'mapping')
        
        def get_parent_for_topic(topic):
            for parent, children in mappings.items():
                if topic in children:
                    return parent
            return None

        # Get all topics from model response
        model_response_topics = mappings.values()
        model_response_topics = sum(model_response_topics, [])

        metrics = []

        for topic in model_response_topics:
            topic_dict = model_response["response"]["stances"].get(topic)
            if topic_dict is None:
                print("id_session", session_ids[i])
                raise ValueError(f"Topic '{topic}' not found in model response.")

            topic_speakers = model_response["response"]["stances"][topic].keys()

            # For each topic, build this dictionary
            # Such that it maps speaker names to a list of stances
            # The first stance is the model response, the second stance is the ground truth
            speakers_stances = {}

            # Get stances for each speaker in model response
            for speaker in topic_speakers:
                normalized = get_normalized_name(speaker)
                speakers_stances[normalized] = [get_label_for_stance(model_response["response"]["stances"][topic][speaker])]
                
            ground_truth_topic = get_parent_for_topic(topic)
            if ground_truth_topic is None:
                raise ValueError(f"Topic '{topic}' not found in ground truth.")
            
            ground_truth_speakers = ground_truth["response"]["stances"][ground_truth_topic].keys()

            # Get stances for each speaker in ground truth
            for speaker in ground_truth_speakers:
                normalized = get_normalized_name(speaker)
                if normalized not in speakers_stances:
                    print("id_session", session_ids[i])                    
                    raise ValueError(f"Speaker '{normalized}' not found in model response.")
                
                label = get_label_for_stance(ground_truth["response"]["stances"][ground_truth_topic][speaker])
                speakers_stances[normalized].append(label)
            
            # if speaker doesnot show up in ground truth, add neutral stance
            for speaker in speakers_stances.keys():
                if len(speakers_stances[speaker]) == 1:
                    speakers_stances[speaker].append(1)

            y_pred = []
            y_true = []

            for speaker, stances in speakers_stances.items():
                y_pred.append(stances[0])
                y_true.append(stances[1])
            
            if not is_uncompressed:
                global_y_pred.extend(y_pred)
                global_y_true.extend(y_true)
            
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, average='weighted', zero_division=0.0)
            recall = recall_score(y_true, y_pred, average='weighted', zero_division=0.0)
            f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0.0)

            metrics.append({
                'topic': topic,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'accuracy': accuracy
            })
        
        # Calculate Metrics Means for all topics in the model response
        precision_mean = np.mean([metric['precision'] for metric in metrics])
        recall_mean = np.mean([metric['recall'] for metric in metrics])
        f1_mean = np.mean([metric['f1'] for metric in metrics])
        accuracy_mean = np.mean([metric['accuracy'] for metric in metrics])

        print(f"Session: {session_ids[i]}")
        print(f"Precision Mean: {precision_mean}")
        print(f"Recall Mean: {recall_mean}")
        print(f"F1 Mean: {f1_mean}")
        print(f"Accuracy Mean: {accuracy_mean}")
        print("=-=" * 10)
        print()

        session_metrics.append({
            'id': session_ids[i],
            'precision': precision_mean,
            'recall': recall_mean,
            'f1': f1_mean,
            'accuracy': accuracy_mean
        })
    
    return session_metrics


small_uncompressed_metrics = calculate_metrics_for_sessions(small_uncompressed, is_uncompressed=True)
small_metrics = calculate_metrics_for_sessions(small)
medium_metrics = calculate_metrics_for_sessions(medium)
big_metrics = calculate_metrics_for_sessions(big)

def calculate_metrics_for_sizes(session_metrics):
    precision_mean = np.mean([metric['precision'] for metric in session_metrics])
    recall_mean = np.mean([metric['recall'] for metric in session_metrics])
    f1_mean = np.mean([metric['f1'] for metric in session_metrics])
    accuracy_mean = np.mean([metric['accuracy'] for metric in session_metrics])

    return {
        'precision': precision_mean,
        'recall': recall_mean,
        'f1': f1_mean,
        'accuracy': accuracy_mean
    }

small_uncompressed_metrics_mean = calculate_metrics_for_sizes(small_uncompressed_metrics)
small_metrics_mean = calculate_metrics_for_sizes(small_metrics)
medium_metrics_mean = calculate_metrics_for_sizes(medium_metrics)
big_metrics_mean = calculate_metrics_for_sizes(big_metrics)

# Save results to CSV

with open('evaluation_stance_results.csv', 'w', newline='') as csvfile:
    fieldnames = ['size', 'precision', 'recall', 'f1', 'accuracy']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'size': 'small_uncompressed', 'precision': f"{small_uncompressed_metrics_mean['precision']:.4f}", 'recall': f"{small_uncompressed_metrics_mean['recall']:.4f}", 'f1': f"{small_uncompressed_metrics_mean['f1']:.4f}", 'accuracy': f"{small_uncompressed_metrics_mean['accuracy']:.4f}"})
    writer.writerow({'size': 'small', 'precision': f"{small_metrics_mean['precision']:.4f}", 'recall': f"{small_metrics_mean['recall']:.4f}", 'f1': f"{small_metrics_mean['f1']:.4f}", 'accuracy': f"{small_metrics_mean['accuracy']:.4f}"})
    writer.writerow({'size': 'medium', 'precision': f"{medium_metrics_mean['precision']:.4f}", 'recall': f"{medium_metrics_mean['recall']:.4f}", 'f1': f"{medium_metrics_mean['f1']:.4f}", 'accuracy': f"{medium_metrics_mean['accuracy']:.4f}"})
    writer.writerow({'size': 'big', 'precision': f"{big_metrics_mean['precision']:.4f}", 'recall': f"{big_metrics_mean['recall']:.4f}", 'f1': f"{big_metrics_mean['f1']:.4f}", 'accuracy': f"{big_metrics_mean['accuracy']:.4f}"})

    overral_metrics = {
        'precision': (small_metrics_mean['precision'] + medium_metrics_mean['precision'] + big_metrics_mean['precision']) / 3,
        'recall': (small_metrics_mean['recall'] + medium_metrics_mean['recall'] + big_metrics_mean['recall']) / 3,
        'f1': (small_metrics_mean['f1'] + medium_metrics_mean['f1'] + big_metrics_mean['f1']) / 3,
        'accuracy': (small_metrics_mean['accuracy'] + medium_metrics_mean['accuracy'] + big_metrics_mean['accuracy']) / 3
    }

    writer.writerow({'size': 'overall', 'precision': f"{overral_metrics['precision']:.4f}", 'recall': f"{overral_metrics['recall']:.4f}", 'f1': f"{overral_metrics['f1']:.4f}", 'accuracy': f"{overral_metrics['accuracy']:.4f}"})


# Plot confusion matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    ax = plt.subplot()
    sns.heatmap(cm, annot=True, ax=ax, fmt='g')

    ax.set_xlabel('Rótulos Previstos')
    ax.set_ylabel('Rótulos Verdadeiros')
    ax.set_title('Matriz de Confusão')
    ax.xaxis.set_ticklabels(['A FAVOR', 'NEUTRO', 'CONTRA'])
    ax.yaxis.set_ticklabels(['A FAVOR', 'NEUTRO', 'CONTRA'])

    plt.savefig('confusion_matrix.png')

plot_confusion_matrix(global_y_true, global_y_pred)

# plot distributions
def plot_distribution(y_true, y_pred):
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    sns.histplot(y_true, ax=ax[0], kde=True)
    ax[0].set_title('Ground Truth Distribution')
    ax[0].set_xlabel('Stance')
    ax[0].set_ylabel('Frequency')

    sns.histplot(y_pred, ax=ax[1], kde=True)
    ax[1].set_title('Model Response Distribution')
    ax[1].set_xlabel('Stance')
    ax[1].set_ylabel('Frequency')

    plt.savefig('distributions.png')

plot_distribution(global_y_true, global_y_pred)