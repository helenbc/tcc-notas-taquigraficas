import json
import csv

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

def read_json_file_to_array(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def read_json_file_to_dict(path):
    with open(path, 'r') as f:
        content = f.read()
        dict = json.loads(content)
    return dict

def get_keys_from_dict(dict):
    model_response_evaluation = dict['model_response_evaluation']['list_latent_topics']
    return model_response_evaluation

def calculate_pressicion(tp,fp):
    return tp/(tp+fp)

def calculate_recall(tp,fn):
    return tp/(tp+fn)

def calculate_f1(pressicion,recall):
    return 2*((pressicion*recall)/(pressicion+recall))

def calculate_accuracy(tp,tn,fp,fn):
    return (tp+tn)/(tp+tn+fp+fn)

def calculate_metrics(tp,tn,fp,fn):
    pressicion = calculate_pressicion(tp,fp)
    recall = calculate_recall(tp,fn)
    f1 = calculate_f1(pressicion,recall)
    accuracy = calculate_accuracy(tp,tn,fp,fn)
    return pressicion, recall, f1, accuracy

def read_tp_tn_fp_fn(dict):
    tp = len(dict['verdadeiro_positivo'])
    tn = len(dict['verdadeiro_negativo'])
    fp = len(dict['falso_positivo'])
    fn = len(dict['falso_negativo'])
    return tp, tn, fp, fn

small_sessions = read_json_file_to_array("./sizes/small_sessions.json")
medium_sessions = read_json_file_to_array("./sizes/medium_sessions.json")
large_sessions = read_json_file_to_array("./sizes/big_sessions.json")

#ground_truth = read_json_file_to_dict("./ground_truth/25518_ground_truth.json")
#dict = get_keys_from_dict(ground_truth)
#print(dict)
#tp, tn, fp, fn = read_tp_tn_fp_fn(dict)
#metrics = calculate_metrics(tp,tn,fp,fn)
#print(metrics)

for session in small:
    session_dict = read_json_file_to_dict(f"./ground_truth/{session}_ground_truth.json")
    dict = get_keys_from_dict(session_dict)
    tp, tn, fp, fn = read_tp_tn_fp_fn(dict)
    metrics = calculate_metrics(tp,tn,fp,fn)
    print(metrics)


def csv_id_size_precision_recall_f1_accuracy():
    with open('metrics_by_session.csv', 'w', newline='') as csvfile:
        fieldnames = ['id', 'size', 'precision', 'recall', 'f1', 'accuracy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for session in small:
            session_dict = read_json_file_to_dict(f"./ground_truth/{session}_ground_truth.json")
            dict = get_keys_from_dict(session_dict)
            tp, tn, fp, fn = read_tp_tn_fp_fn(dict)
            metrics = calculate_metrics(tp,tn,fp,fn)
            writer.writerow({'id': session, 'size': 'small', 'precision': metrics[0], 'recall': metrics[1], 'f1': metrics[2], 'accuracy': metrics[3]})

        for session in medium:
            session_dict = read_json_file_to_dict(f"./ground_truth/{session}_ground_truth.json")
            dict = get_keys_from_dict(session_dict)
            tp, tn, fp, fn = read_tp_tn_fp_fn(dict)
            metrics = calculate_metrics(tp,tn,fp,fn)
            writer.writerow({'id': session, 'size': 'medium', 'precision': metrics[0], 'recall': metrics[1], 'f1': metrics[2], 'accuracy': metrics[3]})

        for session in big:
            session_dict = read_json_file_to_dict(f"./ground_truth/{session}_ground_truth.json")
            dict = get_keys_from_dict(session_dict)
            tp, tn, fp, fn = read_tp_tn_fp_fn(dict)
            metrics = calculate_metrics(tp,tn,fp,fn)
            writer.writerow({'id': session, 'size': 'big', 'precision': metrics[0], 'recall': metrics[1], 'f1': metrics[2], 'accuracy': metrics[3]})

def calculate_metrics_from_csv():
    with open('metrics_by_session.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        #calculate average of each metric
        total_quantity = len(small) + len(medium) + len(big)
        precision = 0
        recall = 0
        f1 = 0
        accuracy = 0
        for row in reader:
            precision += float(row['precision'])
            recall += float(row['recall'])
            f1 += float(row['f1'])
            accuracy += float(row['accuracy'])
        precision = precision / total_quantity
        recall = recall / total_quantity
        f1 = f1 / total_quantity
        accuracy = accuracy / total_quantity
    return precision, recall, f1, accuracy


import csv

def calculate_averages(filename):
    # Dicionários para armazenar as somas das métricas e contagem de entradas
    metrics = {
        'small': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0},
        'medium': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0},
        'big': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0},
        'general': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0}  # Incluir dados gerais
    }

    # Abrir e ler o arquivo CSV
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            size = row['size']
            # Acumular as somas das métricas para cada tamanho e geral
            if size in metrics:
                metrics[size]['precision'] += float(row['precision'])
                metrics[size]['recall'] += float(row['recall'])
                metrics[size]['f1'] += float(row['f1'])
                metrics[size]['accuracy'] += float(row['accuracy'])
                metrics[size]['count'] += 1

            # Acumulações para cálculo geral
            metrics['general']['precision'] += float(row['precision'])
            metrics['general']['recall'] += float(row['recall'])
            metrics['general']['f1'] += float(row['f1'])
            metrics['general']['accuracy'] += float(row['accuracy'])
            metrics['general']['count'] += 1

    # Calcular médias para cada tamanho e geral, armazenar em um novo dicionário
    averages = {}
    for size, data in metrics.items():
        if data['count'] > 0:  # evitar divisão por zero
            averages[size] = {
                'precision': data['precision'] / data['count'],
                'recall': data['recall'] / data['count'],
                'f1': data['f1'] / data['count'],
                'accuracy': data['accuracy'] / data['count']
            }

    return averages

# Exemplo de uso
filename = 'metrics_by_session.csv'
averages = calculate_averages(filename)
for size, avg in averages.items():
    if size == 'general':
        print("General averages across all sessions:")
    else:
        print(f"{size.capitalize()} sessions:")
    for metric, value in avg.items():
        print(f"  Average {metric}: {value:.4f}")


csv_id_size_precision_recall_f1_accuracy()  
print(calculate_metrics_from_csv()) 

# Exemplo de uso
filename = 'metrics_by_session.csv'
averages = calculate_averages(filename)
for size, avg in averages.items():
    print(f"{size.capitalize()} sessions:")
    for metric, value in avg.items():
        print(f"  Average {metric}: {value:.4f}")    



#def count_confussion_matrix(a):
    
