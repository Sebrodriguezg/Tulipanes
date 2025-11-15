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

        # Pre-calcular límites del dibujo
        all_x = [p[0] for path in coordinates for p in path]
        all_y = [-p[1] for path in coordinates for p in path]
        if not all_x or not all_y:
            st.warning("No se encontraron coordenadas para dibujar.")
            return None

        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        ax.set_xlim(x_min - 10, x_max + 10)
        ax.set_ylim(y_min - 10, y_max + 10)


        completed_paths = []

        for path, col in zip(coordinates, colors):
            xs, ys = [], []

            # Dibujar punto por punto
            for (x, y) in path:
                xs.append(x)
                ys.append(-y)

                # Limpiar y re-dibujar todo
                ax.clear()
                ax.set_aspect("equal")
                ax.axis("off")
                ax.set_xlim(x_min - 10, x_max + 10)
                ax.set_ylim(y_min - 10, y_max + 10)

                # Re-dibujar formas ya completadas
                for comp_path, comp_col in completed_paths:
                    ax.fill(comp_path[0], comp_path[1], color=comp_col)

                # Dibujar forma actual
                ax.fill(xs, ys, color=col)


                # Guardar frame
                buf = io.BytesIO()
                plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
                buf.seek(0)
                frames.append(Image.open(buf))

            completed_paths.append(((xs, ys), col))

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
    st.write("Sube un archivo .docx para generar un GIF animado del dibujo que contiene.")

    # Carga de archivo
    uploaded_file = st.file_uploader("Sube tu .docx aquí", type="docx")

    # Botón para generar dibujo de ejemplo
    if st.button("Generar a partir de 'tulipanes.docx'"):
        try:
            with open("tulipanes.docx", "rb") as f:
                coordinates, colors = extract_data(f)
                if coordinates and colors:
                    gif_bytes = create_gif_from_coordinates(coordinates, colors)
                    if gif_bytes:
                        st.image(gif_bytes, caption="Dibujo animado de tulipanes.docx", use_column_width=True)
                else:
                    st.warning("No se encontraron datos válidos en 'tulipanes.docx'.")
        except FileNotFoundError:
            st.error("El archivo 'tulipanes.docx' no se encontró.")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

    # Procesar archivo subido
    if uploaded_file:
        coordinates, colors = extract_data(uploaded_file)
        if coordinates and colors:
            gif_bytes = create_gif_from_coordinates(coordinates, colors)
            if gif_bytes:
                st.image(gif_bytes, caption="Dibujo animado del archivo subido", use_column_width=True)
        else:
            st.warning("No se encontraron datos válidos en el archivo que subiste.")


if __name__ == "__main__":
    main()
