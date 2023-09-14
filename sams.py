from PIL import Image
import numpy as np
import cv2
import pytesseract
import re

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

    # Initialize a list to store the squares
    squares = []
    largest_square = None
    largest_area = 0

    # Iterate through detected contours
    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        area = cv2.contourArea(contour)

        # If the polygon has 4 sides (a square)
        if len(approx) == 4:
            squares.append(approx)
            # If the current square has a larger area, update the largest square
            if area > largest_area:
                largest_area = area
                largest_square = approx

    # Draw the largest square on the original image
    output_image = original_image.copy()
    if largest_square is not None:
        cv2.drawContours(output_image, [largest_square], -1, (0, 255, 0), 3)
        x, y, w, h = cv2.boundingRect(largest_square)

        # Crop the largest square from the original image
        cropped_square = original_image[y:y + 10 + h + 20, x:x + 20 + w + 20]

    # Convert the image to grayscale
    gray = cv2.cvtColor(cropped_square, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges in the image using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize a list to store the squares
    squares = []

    # Iterate through detected contours
    for contour in contours:
        # Approximate the contour to a polygon
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # If the polygon has 4 sides (a square)
        if len(approx) == 4:
            squares.append(approx)

    extracted_lines = []
    student_data = {}

    # Loop through the detected squares
    for square in squares[::-1]:
        # Draw the current square on the original image
        output_image1 = cropped_square.copy()
        cv2.drawContours(output_image1, [square], -1, (0, 255, 0), 3)

        # Convert the square coordinates to a bounding rectangle
        x, y, w, h = cv2.boundingRect(square)

        # Crop the square from the original image
        cropped_square1 = cropped_square[y:y + h, x:x + w]

        extracted_text = pytesseract.image_to_string(cropped_square1).strip()  # OCR code

        if extracted_text:  # If the string is not empty
            extracted_lines.append(extracted_text)
            # Filter out irrelevant lines using simple checks or regular expressions
            student_lines = extracted_text.split("\n")
            valid_lines = [line for line in student_lines if re.search(r'\d{8}', line) and re.search(r'[a-zA-Z]', line)]

            for line in valid_lines:
                # Here, I'm assuming the first 8 digits are the ID and the rest is the name.
                # You may need to adapt this based on your actual data.
                student_id = re.search(r'\d{8}', line).group()
                student_name = re.sub(r'\d{8}', '', line).strip()  # Remove the ID from the line, then strip whitespace
                student_name_clean = re.sub(r'[|“”"\'—-]', '', student_name).strip()
                student_data[student_name_clean] = {"ID": student_id, "Status": "Present"}  # Defaulting status to "Present"

    return student_data