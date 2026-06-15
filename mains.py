import math
import cv2
import pyautogui
import mediapipe as mp
import numpy as np

# --- PARAMÈTRES ---
LARGEUR_REELLE_MAIN = 8.0 
FOCALE_CAMERA = 350
DISTANCE_ACTION = 65
CAM_W, CAM_H = 640, 480       # Taille de la caméra
FRAME_REDUCTION = 120        # Marge de sécurité (Cadre Magique)
LISSAGE = 2.5

# --- INITIALISATION ---
cap = cv2.VideoCapture(0)
cap.set(3, CAM_W)
cap.set(4, CAM_H)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Récupérer la taille de VOTRE écran
SCREEN_W, SCREEN_H = pyautogui.size()

# Variables pour le lissage (éviter que la souris tremble)
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0


# Fonction pour calculer la distance en pixels entre deux points de repère
def calculer_distance_pixels(p1, p2, frame_width, frame_height):
    # Convertit les coordonnées normalisées (0 à 1) en pixels
    x1, y1 = int(p1.x * frame_width), int(p1.y * frame_height)
    x2, y2 = int(p2.x * frame_width), int(p2.y * frame_height)
    # Théorème de Pythagore pour la distance en pixels
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Image non trouvée (caméra vide ?)")
        continue

    cv2.rectangle(image, (FRAME_REDUCTION, FRAME_REDUCTION), 
                 (CAM_W - FRAME_REDUCTION, CAM_H - FRAME_REDUCTION),
                 (255, 0, 255), 2)

    image = cv2.flip(image, 1) # Effet miroir pour une interaction plus naturelle

    # Obtenir les dimensions de l'image
    h, w, _ = image.shape

    # 1. Conversion
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 2. Détection des mains
    results = hands.process(image_rgb)

    # 3. Dessiner les points si une main est détectée
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # -- Récupérer les points d'intérêt --
            p8 = hand_landmarks.landmark[8] # Bout de l'index
            p6 = hand_landmarks.landmark[6] # Milieu de l'index
            p12 = hand_landmarks.landmark[12] # Bout du majeur
            p10 = hand_landmarks.landmark[10] # Milieu du majeur
            p4 = hand_landmarks.landmark[4] # Bout du pouce

            # Index (Point 8) pour bouger
            x8, y8 = hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y
            # Pouce (Point 4) pour cliquer
            x4, y4 = hand_landmarks.landmark[4].x, hand_landmarks.landmark[4].y

            x_index, y_index = int(x8 * CAM_W), int(y8 * CAM_H)
            x_thumb, y_thumb = int(x4 * CAM_W), int(y4 * CAM_H)

            # Convertir en pixels caméra
            x_cam, y_cam = int(p8.x * CAM_W), int(p8.y * CAM_H)

            # Axe X (Horizontal)
            x_mouse = np.interp(x_cam, (FRAME_REDUCTION, CAM_W - FRAME_REDUCTION), (0, SCREEN_W))
            # Axe Y (Vertical)
            y_mouse = np.interp(y_cam, (FRAME_REDUCTION, CAM_H - FRAME_REDUCTION), (0, SCREEN_H))

            curr_x = prev_x + (x_mouse - prev_x) / LISSAGE
            curr_y = prev_y + (y_mouse - prev_y) / LISSAGE

            # Dessine les points et les connexions sur l'image
            mp_drawing.draw_landmarks(
                image, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS)
            
            # Obtenir la base de l'index et la base du petit doigt
            point_5 = hand_landmarks.landmark[5]
            point_17 = hand_landmarks.landmark[17]

            # 1. Calculer la largeur de la main en pixels sur l'écran
            largeur_pixels = calculer_distance_pixels(point_5, point_17, w, h)

            distance_cm = 0
            if largeur_pixels > 0:
                # 2. Estimer la distance de la main à la caméra en cm
                distance_cm = int((LARGEUR_REELLE_MAIN * FOCALE_CAMERA) / largeur_pixels)

            # Note : "p8.y < p6.y" veut dire que le 8 est plus HAUT dans l'image
            index_leve = p8.y < p6.y
            majeur_leve = p12.y < p10.y
            touché = p4.y + 10 >= p8.y

            # --- ÉTAPE 3 : La logique combinée ---
            couleur = (0, 0, 255) # Rouge par défaut
            message = f"Distance: {distance_cm}cm"
     
            # --- DÉPLACEMENT ---
            # On déplace la souris (pyautogui gère l'écran)
            pyautogui.moveTo(curr_x, curr_y)

            # Mettre à jour les anciennes positions
            prev_x, prev_y = curr_x, curr_y

            # Dessiner un cercle sur l'index
            cv2.circle(image, (x_cam, y_cam), 15, (255, 0, 255), cv2.FILLED)


            if majeur_leve and distance_cm < DISTANCE_ACTION:
                # Si majeur levé ET main proche
                couleur = (255, 0, 0) # Bleu
                message = "c'est pas cool :c"
                cv2.circle(image, (150, 50), 30, (255, 0, 0), -1) # Un rond bleu s'allume

            # -- CLIC GAUCHE ---
            # Dessiner les points
            cv2.circle(image, (x_index, y_index), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(image, (x_thumb, y_thumb), 15, (255, 0, 255), cv2.FILLED)
            
            # On dessine une ligne entre le pouce et l'index pour visualiser
            cv2.line(image, (x_thumb, y_thumb), (x_index, y_index), (255, 0, 255), 3)
            
            distance = math.hypot(x_index - x_thumb, y_index - y_thumb)

            if distance < 30: # Seuil de clic (ajustable)
                pyautogui.click()

            # Affichage
            cv2.putText(image, message, (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, couleur, 2)



    # Afficher (flip pour effet miroir)
    cv2.imshow('Suivi des mains (Quitter avec Q)', image)

    # Quitter si on appuie sur la touche 'q'
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()