import numpy as np
import scipy.stats as stats
import csv
import tkinter as tk
from tkinter import filedialog, messagebox


def leer_archivo(archivo):
    with open(archivo, "r") as f:
        reader = csv.reader(f)
        numeros = [float(item) for row in reader for item in row]
    return numeros


def prueba_chi_cuadrado(data, dist_name, params):
    # Obtener el histograma de los datos
    hist, bin_edges = np.histogram(data, bins="auto", density=False)

    # Obtener las observaciones esperadas según la distribución
    if dist_name == "uniform":
        dist = stats.uniform(loc=params[0], scale=params[1])
    elif dist_name == "norm":
        dist = stats.norm(loc=params[0], scale=params[1])

    # Calcular las frecuencias esperadas para cada bin
    expected_freq = dist.cdf(bin_edges[1:]) - dist.cdf(bin_edges[:-1])
    expected_freq *= len(data)

    # Asegurarse de que las sumas coincidan
    expected_freq *= hist.sum() / expected_freq.sum()

    chi2, p_value = stats.chisquare(hist, expected_freq)
    return chi2, p_value


def prueba_ks(data, dist_name, params):
    if dist_name == "uniform":
        dist = stats.uniform(loc=params[0], scale=params[1])
    elif dist_name == "norm":
        dist = stats.norm(loc=params[0], scale=params[1])

    ks_stat, p_value = stats.kstest(data, dist.cdf)
    return ks_stat, p_value


def ajustar_distribuciones(data):
    # Ajustar distribución uniforme
    min_val, max_val = min(data), max(data)
    params_uniform = (min_val, max_val - min_val)

    # Ajustar distribución normal
    mean, std = np.mean(data), np.std(data)
    params_norm = (mean, std)

    return params_uniform, params_norm


def evaluar_distribuciones(data):
    params_uniform, params_norm = ajustar_distribuciones(data)

    chi2_uniform, p_chi2_uniform = prueba_chi_cuadrado(data, "uniform", params_uniform)
    chi2_norm, p_chi2_norm = prueba_chi_cuadrado(data, "norm", params_norm)

    ks_uniform, p_ks_uniform = prueba_ks(data, "uniform", params_uniform)
    ks_norm, p_ks_norm = prueba_ks(data, "norm", params_norm)

    resultados = {
        "uniforme": {"chi2": p_chi2_uniform, "ks": p_ks_uniform},
        "normal": {"chi2": p_chi2_norm, "ks": p_ks_norm},
    }

    print("Resultados de las pruebas:")
    for dist, res in resultados.items():
        print(f"Distribución {dist.capitalize()}:")
        print(f"  Chi-cuadrado p-valor: {res['chi2']}")
        print(f"  KS p-valor: {res['ks']}")

    if resultados["uniforme"]["chi2"] > 0.05 and resultados["uniforme"]["ks"] > 0.05:
        return "uniforme"
    elif resultados["normal"]["chi2"] > 0.05 and resultados["normal"]["ks"] > 0.05:
        return "normal"
    else:
        return "ninguna"


def generar_archivo(distribucion, tamano, archivo):
    if distribucion == "uniforme":
        data = np.random.uniform(0, 1, tamano)
    elif distribucion == "normal":
        data = np.random.normal(0, 1, tamano)

    with open(archivo, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Prueba de distribuciones para un conjunto de números."
    )
    parser.add_argument("archivo", type=str, help="Ruta del archivo de entrada")
    parser.add_argument(
        "--generar", type=str, help='Generar archivo: "uniforme" o "normal"'
    )
    parser.add_argument(
        "--tamano", type=int, help="Tamaño del conjunto de datos a generar"
    )
    args = parser.parse_args()

    if args.generar:
        if args.generar in ["uniforme", "normal"] and args.tamano:
            generar_archivo(args.generar, args.tamano, args.archivo)
            print(f"Archivo generado: {args.archivo}")
        else:
            print(
                "Debe especificar el tipo de distribución ('uniform' o 'normal') y el tamaño del conjunto de datos."
            )
    else:
        data = leer_archivo(args.archivo)
        resultado = evaluar_distribuciones(data)
        print(f"El conjunto de números se asemeja más a una distribución {resultado}.")
