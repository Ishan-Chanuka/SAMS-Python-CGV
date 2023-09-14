from PIL import Image
import numpy as np
import cv2
import pytesseract
import re
import pyodbc

def img_to_gray(image_path):
    image = Image.open(image_path)
    gray_image = image.convert("L")

    gray_array = np.array(gray_image)
    return gray_array

def new_process_image(image_path):
    original_image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = img_to_gray(image_path)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges in the image using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    squares = []
    largest_square = None
    largest_area = 0

    for contour in contours:
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        area = cv2.contourArea(contour)

        if len(approx) == 4:
            squares.append(approx)
            if area > largest_area:
                largest_area = area
                largest_square = approx

    output_image = original_image.copy()
    if largest_square is not None:
        cv2.drawContours(output_image, [largest_square], -1, (0, 255, 0), 3)
        x, y, w, h = cv2.boundingRect(largest_square)

        cropped_square = original_image[y:y + 10 + h + 20, x:x + 20 + w + 20]

    # Convert the image to grayscale
    gray = cv2.cvtColor(cropped_square, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges in the image using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    squares = []

    for contour in contours:
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            squares.append(approx)

    extracted_lines = []
    student_data = {}

    for square in squares[::-1]:
        output_image1 = cropped_square.copy()
        cv2.drawContours(output_image1, [square], -1, (0, 255, 0), 3)

        x, y, w, h = cv2.boundingRect(square)

        cropped_square1 = cropped_square[y:y + h, x:x + w]

        extracted_text = pytesseract.image_to_string(cropped_square1).strip()

        if extracted_text:
            extracted_lines.append(extracted_text)
            student_lines = extracted_text.split("\n")
            valid_lines = [line for line in student_lines if re.search(r'\d{8}', line) and re.search(r'[a-zA-Z]', line)]

            for line in valid_lines:
                student_id = re.search(r'\d{8}', line).group()
                student_name = re.sub(r'\d{8}', '', line).strip()
                student_name_clean = re.sub(r'[|“”"\'—-]', '', student_name).strip()
                student_data[student_name_clean] = {"ID": student_id, "Status": "Present"}

    return student_data


def parse_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    student_info = {}
    for student in root.findall('student'):
        index = student.get('index')
        name = student.find('name').text
        student_info[index] = name
    return student_info

def store_to_db(data):
    conn = pyodbc.connect(
        r'Driver={ODBC Driver 17 for SQL Server};'
        r'Server=ISHAN\SQLEXPRESS;'
        r'Database=AttendanceDb;'
        r'UID=ick;'
        r'PWD=Ishan,1998'
    )

    c = conn.cursor()
    c.execute("IF OBJECT_ID('attendance', 'U') IS NULL CREATE TABLE attendance (ID NVARCHAR(50), Name NVARCHAR(50), "
              "Status NVARCHAR(50))")

    try:
        for name, info in data.items():
            insert_query = "INSERT INTO attendance (name, id, status) VALUES (?, ?, ?)"
            c.execute(insert_query, name, info['ID'], info['Status'])

        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        c.close()
        conn.close()

def main(xml_path, image_path):
    processed_data = new_process_image(image_path)
    student_info = parse_xml(xml_path)

    # dummy_data = {
    #     'MS Dilshanika Perera  hl': {'ID': '10000409', 'Status': 'Present'},
    #     'C W M AShehan Abeyrathne a.': {'ID': '10009301', 'Status': 'Present'},
    #     'BAKM Chithrananda  i': {'ID': '10009302', 'Status': 'Present'},
    #     'W Shashini Minosha De Silva': {'ID': '10009303', 'Status': 'Present'},
    #     'K  Udara Maduranga Liyanage i': {'ID': '10009304', 'Status': 'Present'},
    #     'a  Hansa Anuradha Wickramanayake': {'ID': '10009306', 'Status': 'Present'}
    # }

    # print(processed_data)

    store_to_db(processed_data)

if __name__ == "__main__":
    main('info.xml', '4.jpg')