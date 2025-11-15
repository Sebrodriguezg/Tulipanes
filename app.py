import streamlit as st
import turtle as tu
import re
import docx
from PIL import Image
import io

def extract_data(file):
    """Extracts coordinates and colors from a .docx file."""
    try:
        data = docx.Document(file)
        coordinates = []
        colors = []

        for i in data.paragraphs:
            try:
                coord_stg_tup = re.findall(r'\([-+]?\d*\.\d*(?:[eE][-+]?\d+)? ?\, ?[-+]?\d*\.\d*(?:[eE][-+]?\d+)?\)', i.text)
                coord_num_tup = []
                color_stg_tup = re.findall(r'\([-+]?\d*\.\d*(?:[eE][-+]?\d+)? ?\, ?[-+]?\d*\.\d*(?:[eE][-+]?\d+)? ?\, ?[-+]?\d*\.\d*(?:[eE][-+]?\d+)?\)', i.text)
                color_val = re.findall(r'[-+]?\d*\.\d*', color_stg_tup[0])
                color_val_lst = [float(k) for k in color_val]
                colors.append(tuple(color_val_lst))

                for j in coord_stg_tup:
                    coord_pos = re.findall(r'[-+]?\d*\.\d*', j)
                    coord_num_lst = [float(k) for k in coord_pos]
                    coord_num_tup.append(tuple(coord_num_lst))

                coordinates.append(coord_num_tup)
            except:
                continue

        return coordinates, colors
    except Exception as e:
        st.error(f"Error reading .docx file: {e}")
        return None, None

def create_drawing(coordinates, colors):
    """Creates a drawing from coordinates and colors and returns it as a PNG image."""
    try:
        # Create a new turtle screen for each drawing
        screen = tu.Screen()
        screen.setup(width=800, height=600)  # Set a default screen size

        pen = tu.Turtle()
        pen.speed(0)
        tu.hideturtle()

        for i in range(len(coordinates)):
            draw = 1
            path = coordinates[i]
            col = colors[i]
            pen.color(col)
            pen.begin_fill()
            for order_pair in path:
                x, y = order_pair
                y = -1 * y
                if draw:
                    pen.up()
                    pen.goto(x, y)
                    pen.down()
                    draw = 0
                else:
                    pen.goto(x, y)
            pen.end_fill()

        # Save the drawing to a PostScript file
        ps_file = "drawing.ps"
        screen.getcanvas().postscript(file=ps_file)

        # Convert the PostScript file to a PNG image
        img = Image.open(ps_file)

        # Crop the image to remove unnecessary whitespace
        cropped_img = img.crop(img.getbbox())

        img_byte_arr = io.BytesIO()
        cropped_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Clear the screen and reset turtle state
        screen.clear()
        tu.TurtleScreen._RUNNING = True

        return img_byte_arr
    except Exception as e:
        st.error(f"Error creating drawing: {e}")
        return None

def main():
    st.title("Turtle Drawing Generator")
    st.write("This application generates a drawing from a .docx file.")

    uploaded_file = st.file_uploader("Choose a .docx file", type="docx")

    if st.button("Generate Drawing"):
        if uploaded_file is not None:
            coordinates, colors = extract_data(uploaded_file)
            if coordinates and colors:
                image = create_drawing(coordinates, colors)
                if image:
                    st.image(image, caption="Generated Drawing", use_column_width=True)
            else:
                st.warning("No valid data found in the uploaded file.")
        else:
            with open("tulipanes.docx", "rb") as f:
                coordinates, colors = extract_data(f)
                if coordinates and colors:
                    image = create_drawing(coordinates, colors)
                    if image:
                        st.image(image, caption="Generated Drawing", use_column_width=True)
                else:
                    st.error("Could not generate the drawing from the default file.")

if __name__ == "__main__":
    main()
