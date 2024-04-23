import csv

def calculate_averages(filename):
    # Dicionários para armazenar as somas das métricas e contagem de entradas
    metrics = {
        'small': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0},
        'medium': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0},
        'big': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0, 'count': 0}
    }

    # Abrir e ler o arquivo CSV
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            size = row['size']
            # Acumular as somas das métricas para cada tamanho
            if size in metrics:
                metrics[size]['precision'] += float(row['precision'])
                metrics[size]['recall'] += float(row['recall'])
                metrics[size]['f1'] += float(row['f1'])
                metrics[size]['accuracy'] += float(row['accuracy'])
                metrics[size]['count'] += 1

    # Calcular médias para cada tamanho e armazenar em um novo dicionário
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
    print(f"{size.capitalize()} sessions:")
    for metric, value in avg.items():
        print(f"  Average {metric}: {value:.4f}")
