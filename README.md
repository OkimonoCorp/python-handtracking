# 🖐️ Détection de Mouvements (Handtracking) en Python

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
</p>

Ce script est une expérimentation en vision par ordinateur (Computer Vision). Il permet de détecter et de suivre les mouvements de la main en temps réel via un flux vidéo ou une webcam.

---

## ⚙️ Comment ça marche ?

Le projet analyse les images en temps réel pour repérer des points de repère spécifiques (landmarks) sur la main humaine. Il calcule ensuite la position de ces points dans l'espace, ce qui permet d'interpréter des gestes ou de suivre la position des doigts avec précision.

## 📸 Démonstration

> <img width="647" height="508" alt="image1HandTracking" src="https://github.com/user-attachments/assets/038b839b-9ffa-4bf1-8aa9-7ad9ad0db7c0" />
<img width="633" height="512" alt="image2Handtracking" src="https://github.com/user-attachments/assets/b2da6825-3754-49f6-9051-a20164d2389f" />

---

## 🛠️ Installation et Prérequis

Assurez-vous d'avoir installé **Python 3, opencv-python, mediapipe** sur votre machine.

1. Clonez ce dépôt :
   ```bash
   git clone [https://github.com/OkimonoCorp/python-handtracking.git](https://github.com/OkimonoCorp/python-handtracking.git)
