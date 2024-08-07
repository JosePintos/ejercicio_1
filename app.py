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

    # Para que las sumas de las frecuencias coincidan, si no tira error
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
    # Parametros para dist uniforme
    min_val, max_val = min(data), max(data)
    params_uniform = (min_val, max_val - min_val)

    # Parametros para dist normal
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

    resultado_final = "Resultados de las pruebas:\n"
    for dist, res in resultados.items():
        resultado_final += f"Distribución {dist.capitalize()}:\n"
        resultado_final += f"  Chi-cuadrado p-valor: {res['chi2']}\n"
        resultado_final += f"  KS p-valor: {res['ks']}\n"

    if resultados["uniforme"]["chi2"] > 0.05 and resultados["uniforme"]["ks"] > 0.05:
        return "uniforme", resultado_final
    elif resultados["normal"]["chi2"] > 0.05 and resultados["normal"]["ks"] > 0.05:
        return "normal", resultado_final
    else:
        return "ninguna", resultado_final


def generar_archivo(distribucion, size, archivo):
    if distribucion == "uniform":
        data = np.random.uniform(0, 1, size)
    elif distribucion == "normal":
        data = np.random.normal(0, 1, size)

    with open(archivo, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(data)


def seleccionar_archivo():
    archivo = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if archivo:
        data = leer_archivo(archivo)
        resultado, detalles = evaluar_distribuciones(data)
        messagebox.showinfo(
            "Resultado",
            f"El conjunto de números se asemeja más a una distribución {resultado}.\n\n{detalles}",
        )


def generar_datos():
    distribucion = distribucion_var.get()
    size = int(size_var.get())
    archivo = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Text files", "*.txt")]
    )
    if archivo:
        generar_archivo(distribucion, size, archivo)
        messagebox.showinfo("Archivo Generado", f"Archivo generado: {archivo}")


# Crear la ventana principal
root = tk.Tk()
root.title("Análisis de Distribuciones")

# Crear widgets
label1 = tk.Label(root, text="Seleccione un archivo .txt para analizar:")
label1.pack(pady=10)
boton_seleccionar = tk.Button(
    root, text="Seleccionar Archivo", command=seleccionar_archivo
)
boton_seleccionar.pack(pady=5)

label2 = tk.Label(root, text="Generar archivo con datos distribuidos:")
label2.pack(pady=10)
distribucion_var = tk.StringVar(value="uniform")
radio_uniforme = tk.Radiobutton(
    root, text="Uniforme", variable=distribucion_var, value="uniform"
)
radio_normal = tk.Radiobutton(
    root, text="Normal", variable=distribucion_var, value="normal"
)
radio_uniforme.pack()
radio_normal.pack()

size_var = tk.StringVar(value="1000")
label_size = tk.Label(root, text="Tamaño del conjunto de datos:")
label_size.pack(pady=5)
entry_size = tk.Entry(root, textvariable=size_var)
entry_size.pack(pady=5)

boton_generar = tk.Button(root, text="Generar Archivo", command=generar_datos)
boton_generar.pack(pady=10)

# Iniciar simulador
root.mainloop()
