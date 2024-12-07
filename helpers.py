"""Tämä moduuli sisältää apufunktioita kuvankäsittelyyn ja tietojen muuntamiseen.

Sisältää funktiot:
- convert_numpy_types: Muuntaa NumPy-tyypit Pythonin perusdatatyypeiksi.
- load_class_info: Lataa luokkien nimet ja määrän data.yaml-tiedostosta.
- get_center: Laskee bounding boxin keskipisteen.
- is_inside: Tarkistaa, onko sisemmän laatikon keskipiste ulomman laatikon sisällä.
- draw_transparent_box: Piirtää puoliksi läpinäkyvän laatikon kuvaan.
"""

import numpy as np
import cv2
import yaml


def convert_numpy_types(obj):
    """
    Muuntaa NumPy-tyypit Pythonin perusdatatyypeiksi.

    Tämä funktio käy rekursiivisesti läpi annetun objektin ja muuntaa kaikki
    NumPy-tyypit vastaaviksi Pythonin perusdatatyypeiksi, jotta ne voidaan
    esimerkiksi sarjoittaa JSON-muotoon.

    Args:
        obj: Muunnettava objekti, joka voi olla sanakirja, lista, NumPy-tyyppi
            tai mikä tahansa muu objekti.

    Returns:
        Muunnettu objekti, jossa kaikki NumPy-tyypit on korvattu Pythonin tyypeillä.
    """
    if isinstance(obj, dict):
        # Käy läpi sanakirjan avaimet ja arvot rekursiivisesti
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Käy läpi listan alkiot rekursiivisesti
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.integer):
        # Muunna NumPy-kokonaisluku Pythonin int-tyypiksi
        return int(obj)
    elif isinstance(obj, np.floating):
        # Muunna NumPy-liukuluku Pythonin float-tyypiksi
        return float(obj)
    elif isinstance(obj, np.ndarray):
        # Muunna NumPy-taulukko Pythonin listaksi
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.complexfloating):
        return complex(obj)
    else:
        # Palauta objekti sellaisenaan, jos se ei ole NumPy-tyyppi
        return obj


def load_class_info(yaml_path):
    """
    Lataa luokkien nimet ja luokkien määrän YAML-tiedostosta.

    Args:
        yaml_path (str): Polku YAML-tiedostoon, joka sisältää luokkien tiedot.

    Returns:
        tuple: (class_names, num_classes)
            - class_names (list): Lista luokkien nimistä.
            - num_classes (int): Luokkien kokonaismäärä.
    """
    try:
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
        return data['names'], data['nc']
    except FileNotFoundError:
        raise FileNotFoundError(f"Tiedostoa {yaml_path} ei löydy.")
    except KeyError as e:
        raise KeyError(f"Avain {e} puuttuu tiedostosta {yaml_path}.")


def get_center(bbox):
    """
    Laskee bounding boxin keskipisteen.

    Args:
        bbox (tuple): Bounding boxin koordinaatit muodossa (x_min, y_min, x_max, y_max).

    Returns:
        tuple: (center_x, center_y)
            - center_x (float): Keskipisteen x-koordinaatti.
            - center_y (float): Keskipisteen y-koordinaatti.
    """
    x_min, y_min, x_max, y_max = bbox
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2
    return center_x, center_y


def is_inside(inner_box, outer_box):
    """
    Tarkistaa, onko inner_boxin keskipiste outer_boxin sisällä.

    Args:
        inner_box (tuple): Sisemmän laatikon koordinaatit (x1, y1, x2, y2).
        outer_box (tuple): Ulomman laatikon koordinaatit (X1, Y1, X2, Y2).

    Returns:
        bool: True, jos keskipiste on sisällä, muuten False.
    """
    # Hae inner_boxin keskipiste
    mid_x, mid_y = get_center(inner_box)

    # Hae outer_boxin koordinaatit
    X1, Y1, X2, Y2 = outer_box

    # Tarkista, onko keskipiste outer_boxin sisällä
    result = X1 <= mid_x <= X2 and Y1 <= mid_y <= Y2
    # print(f"Tarkistetaan, onko laatikko {inner_box} sisällä laatikossa {outer_box}: {result}")
    return result


def draw_transparent_box(img, x1, y1, x2, y2, color, alpha):
    """
    Piirtää puoliksi läpinäkyvän laatikon kuvaan.

    Args:
        img (numpy.ndarray): Kuva, johon laatikko piirretään.
        x1 (int): Laatikon vasemman yläkulman x-koordinaatti.
        y1 (int): Laatikon vasemman yläkulman y-koordinaatti.
        x2 (int): Laatikon oikean alakulman x-koordinaatti.
        y2 (int): Laatikon oikean alakulman y-koordinaatti.
        color (tuple): Laatikon väri (B, G, R).
        alpha (float): Läpinäkyvyyden aste välillä [0, 1].

    Returns:
        None

    Raises:
        ValueError: Jos koordinaatit eivät muodosta kelvollista suorakulmiota.
    """
    # Varmista, että koordinaatit ovat kelvolliset
    if x1 >= x2 or y1 >= y2:
        raise ValueError("Koordinaattien on täytettävä ehto x1 < x2 ja y1 < y2.")
    # Varmista, että koordinaatit ovat kuvan rajojen sisällä
    height, width = img.shape[:2]
    x1 = max(0, min(x1, width))
    x2 = max(0, min(x2, width))
    y1 = max(0, min(y1, height))
    y2 = max(0, min(y2, height))

    # Luo kopio kuvasta piirtoa varten
    overlay = img.copy()
    # Piirrä täytetty suorakulmio overlay-kuvaan
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    # Yhdistä overlay alkuperäiseen kuvaan käyttäen läpinäkyvyyttä
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

