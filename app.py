import streamlit as st
import re
import docx
import matplotlib.pyplot as plt
from PIL import Image
import io


# ============================================================
# EXTRACTOR DE DATOS DESDE .DOCX (VERSIÓN CORRECTA)
# ============================================================

def extract_data(file):
    """Extract coordinates and colors from a .docx file, compatible with tulipanes.py format."""
    try:
        data = docx.Document(file)
        coordinates = []
        colors = []

        for paragraph in data.paragraphs:

            # Buscar color (siempre primer tuple de 3 números)
            color_match = re.findall(
                r'\([-+]?\d*\.\d* ?\, ?[-+]?\d*\.\d* ?\, ?[-+]?\d*\.\d*\)',
                paragraph.text
            )

            if not color_match:
                continue

            # Extraer color
            rgb_values = re.findall(r'[-+]?\d*\.\d*', color_match[0])
            rgb_tuple = tuple(float(v) for v in rgb_values)
            colors.append(rgb_tuple)

            # Buscar coordenadas (solo tuples con 2 números)
            coord_matches = re.findall(
                r'\([-+]?\d*\.\d* ?\, ?[-+]?\d*\.\d*\)',
                paragraph.text
            )

            coord_list = []
            for c in coord_matches:
                vals = re.findall(r'[-+]?\d*\.\d*', c)
                if len(vals) == 2:
                    coord_list.append( (float(vals[0]), float(vals[1])) )

            coordinates.append(coord_list)

        return coordinates, colors

    except Exception as e:
        st.error(f"Error al leer el archivo .docx: {e}")
        return None, None



# ============================================================
# CREAR GIF ANIMADO
# ============================================================

def create_gif_from_coordinates(coordinates, colors, fps=20):
    """Genera un GIF animado mostrando cómo se dibuja la figura paso a paso."""
    frames = []

    try:
        fig, ax = plt.subplots(figsize=(6, 6))

        ax.set_aspect("equal")
        ax.axis("off")

        for path, col in zip(coordinates, colors):

            xs = []
            ys = []

            # Dibujar punto por punto
            for (x, y) in path:
                xs.append(x)
                ys.append(-y)

                ax.clear()
                ax.set_aspect("equal")
                ax.axis("off")
                ax.fill(xs, ys, color=col)

                buf = io.BytesIO()
                plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
                buf.seek(0)
                frames.append(Image.open(buf))

        plt.close()

        # Guardar GIF
        gif_bytes = io.BytesIO()
        frames[0].save(
            gif_bytes,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=int(1000 / fps),
            loop=0
        )
        gif_bytes.seek(0)
        return gif_bytes

    except Exception as e:
        st.error(f"Error creando el GIF: {e}")
        return None



# ============================================================
# APLICACIÓN STREAMLIT
# ============================================================

def main():
    st.title("Generador de Figuras Animadas desde .docx")
    st.write("La aplicación interpreta coordenadas y colores desde un archivo .docx y genera un GIF del dibujo animado.")

    uploaded_file = st.file_uploader("Sube un archivo .docx", type="docx")

    if st.button("Generar dibujo"):
        if uploaded_file:
            coordinates, colors = extract_data(uploaded_file)
        else:
            try:
                with open("tulipanes.docx", "rb") as f:
                    coordinates, colors = extract_data(f)
            except:
                st.error("No subiste archivo y tampoco existe 'tulipanes.docx'.")
                return

        if coordinates and colors:
            gif_bytes = create_gif_from_coordinates(coordinates, colors)

            if gif_bytes:
                st.image(gif_bytes, caption="Dibujo animado", use_column_width=True)
        else:
            st.warning("No se encontraron datos válidos en el archivo.")


if __name__ == "__main__":
    main()
