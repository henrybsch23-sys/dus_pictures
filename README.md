# dus_pictures

Este repositorio contiene un flujo de trabajo para analizar imágenes de **Doppler Ultrasound (DUS)**.  
El proceso está dividido en dos archivos principales: `Step1_margin.py` y `Step2-5.ipynb`.  
A partir de una imagen de ultrasonido en formato `.jpg`, el flujo permite seleccionar un área de interés (ROI), extraer las líneas relevantes (flujo sanguíneo), generar datos numéricos y graficarlos.

---

## 🧩 Archivos principales

### 1️⃣ Step1_margin.py
Este script se utiliza para **definir la región de interés (ROI)** dentro de una imagen de ultrasonido.

#### Uso:
1. Abre el archivo `Step1_margin.py`.
2. En la **línea 22**, reemplaza la variable `img_path` con el nombre de la imagen que quieras usar, por ejemplo:
   ```python
   img_path = "pic_4.jpg"
   ```
3. Ejecuta el script dentro de tu entorno virtual o entorno local de Python.
4. Se abrirá una ventana interactiva donde podrás **seleccionar con el ratón el área de interés** (idealmente la zona donde se observa el flujo sanguíneo).
5. Al finalizar, en la terminal aparecerán las coordenadas del ROI, por ejemplo:
   ```bash
   ROI set: {'x0': 47, 'y0': 671, 'x1': 1187, 'y1': 889}
   ```
6. Copia estos valores, ya que los usarás en el siguiente paso.

---

### 2️⃣ Step2-5.ipynb
Este cuaderno Jupyter ejecuta los pasos **2 a 5** del flujo de trabajo. Cada bloque corresponde a una etapa del procesamiento.

#### Paso 2 – Extraer la imagen
- Reemplaza la variable `ROOT_NAME` por el nombre del archivo (sin `.jpg`), por ejemplo:
  ```python
  ROOT_NAME = "pic_4"
  ```
- Reemplaza la variable `ROI` por las coordenadas que copiaste del paso anterior:
  ```python
  ROI = {'x0': 108, 'y0': 667, 'x1': 1186, 'y1': 894}
  ```
- Ejecuta la celda.  
  El resultado será una imagen recortada con el nombre:
  ```
  pic_4_crop.png
  ```

#### Paso 3 – Extraer las líneas
- Ejecuta la celda “Extract lines”.  
  Aquí se detectan las líneas de color **amarillo** y **blanco** del flujo.  
  El resultado será:
  ```
  pic_4_lines.png
  ```

#### Paso 4 – Convertir a CSV
- Configura las variables:
  ```python
  DURATION_SEC = <duración_en_segundos>
  V_PEAK = <velocidad_pico>
  ```
  Estas variables definen el periodo total de tiempo de la imagen y la velocidad máxima registrada.  
- Ejecuta la celda para generar un archivo CSV con los valores numéricos extraídos:
  ```
  pic_4_lines.csv
  ```

#### Paso 5 – Graficar los puntos del CSV
- Ejecuta la última celda.  
  Se generará un gráfico de velocidad en función del tiempo, guardado como:
  ```
  pic_4_plot.png
  ```

---

## 📂 Estructura de salida
| Etapa | Descripción | Archivo de salida |
|:------|:-------------|:------------------|
| Paso 2 | Imagen recortada | `pic_4_crop.png` |
| Paso 3 | Líneas extraídas | `pic_4_lines.png` |
| Paso 4 | Datos CSV | `pic_4_lines.csv` |
| Paso 5 | Gráfico final | `pic_4_plot.png` |

Todos los archivos generados adoptan el nombre base del archivo configurado en `ROOT_NAME`.

---

## ⚙️ Requisitos
- Python 3.x
- Entorno virtual (recomendado)
- Librerías necesarias (ver `requirements.txt`)

### Instalación:
```bash
pip install -r requirements.txt
```

---

## 🚀 Ejemplo de uso completo

1. Ejecutar `Step1_margin.py` con la imagen deseada (`pic_4.jpg`).
2. Seleccionar la región de interés y copiar las coordenadas del ROI.
3. Abrir `Step2-5.ipynb` en Jupyter Notebook.
4. Configurar `ROOT_NAME` y `ROI` en el bloque del **Paso 2**.
5. Ejecutar las celdas del paso 2 al 5 en orden.
6. Verifica los archivos generados en la carpeta del proyecto.

---

## 🩺 Notas adicionales
- El flujo está diseñado para imágenes Doppler Ultrasound (DUS) con visualización de flujo sanguíneo.
- Cada paso es independiente y permite verificar visualmente el resultado intermedio.
- Si cambias de imagen, asegúrate de repetir el **Step 1** y actualizar los valores de `ROOT_NAME` y `ROI` en el cuaderno.

---

**Autor:** Henry Serpa
**Proyecto:** `dus_pictures` - Análisis de imágenes Doppler Ultrasound
