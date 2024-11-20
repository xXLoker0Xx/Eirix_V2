from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import base64
import mediapipe as mp
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "¡Hola desde el backend!"}), 200

@app.route('/api/echo', methods=['POST'])
def echo_data():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    return jsonify({
        "message": "Datos recibidos correctamente",
        "data": data
    }), 200


UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

mp_face_mesh = mp.solutions.face_mesh

def process_image_with_mediapipe(image_path, output_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("No se pudo leer la imagen.")

    # Convert the image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Initialize Mediapipe Face Mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        # Process the image
        results = face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            raise ValueError("No se detectaron rostros en la imagen.")

        # Draw the face landmarks on the image
        for face_landmarks in results.multi_face_landmarks:
            for landmark in face_landmarks.landmark:
                x = int(landmark.x * image.shape[1])
                y = int(landmark.y * image.shape[0])
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
    # Save the processed image
    cv2.imwrite(output_path, image)
    return image


    

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the original image
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    proc_file_path = os.path.join(PROCESSED_FOLDER, file.filename)
    file.save(file_path)

    # Process the image with Mediapipe
    try:
        processed_image = process_image_with_mediapipe(file_path,proc_file_path)
        # Encode the processed image to base64
        _, buffer = cv2.imencode('.jpg', processed_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "message": "File processed successfully",
        "processed_image": encoded_image  # Return base64 encoded image
    }), 200


def process_posture_with_mediapipe(image_path, output_path):
    # Cargar la imagen
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("No se pudo leer la imagen.")

    # Convertir a RGB para Mediapipe
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Procesar la imagen con Mediapipe Pose
    results = pose.process(rgb_image)

    if not results.pose_landmarks:
        raise ValueError("No se detectaron puntos clave de postura en la imagen.")

    # Dibujar los puntos clave y las conexiones
    annotated_image = image.copy()
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing.draw_landmarks(
        annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
        mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
    )

    cv2.imwrite(output_path, annotated_image)
    return annotated_image

@app.route('/api/P_upload', methods=['POST'])
def p_upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Guardar la imagen original
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    proc_file_path = os.path.join(PROCESSED_FOLDER, file.filename)
    file.save(file_path)

    # Procesar la postura con Mediapipe
    try:
        processed_image = process_posture_with_mediapipe(file_path,proc_file_path)

        # Codificar la imagen procesada a base64
        _, buffer = cv2.imencode('.jpg', processed_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "message": "Postura procesada exitosamente",
        "processed_image": encoded_image  # Imagen procesada en base64
    }), 200


""" @app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200 """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
