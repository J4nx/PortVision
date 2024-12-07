"""Tämä skripti sisältää funktioita LAN-porttien ja LAN-porttipinojen bounding boxien jälkikäsittelyyn."""

import cv2
import numpy as np
import json
from json_generator import generate_switch_json
from helpers import (
    convert_numpy_types,
    is_inside,
    draw_transparent_box,
    load_class_info
)

# Lue luokkien nimet ja luokkien määrä tiedostosta data.yaml
class_names, nc = load_class_info("data.yaml")

# Määritä kiinteä värikartta jokaiselle luokalle sen indeksin perusteella
class_colors = {
    0: (255, 0, 0),       # Kaapeli (Punainen)
    1: (255, 255, 0),     # LAN-portti (Keltainen)
    2: (255, 255, 255),   # LAN-porttipino (Valkoinen)
    3: (0, 0, 255)        # Kytkin (Sininen)
}


def draw_bboxes(image, results, box_thickness=2, font_scale=0.8, alpha=0.6):
    """
    Piirtää bounding boxit ja luo JSON-tulosteen tunnistetuille objekteille.

    Args:
        image (PIL.Image): Syötekuva.
        results (list): Lista tunnistustuloksista.
        box_thickness (int, optional): Bounding boxien viivan paksuus. Oletus 2.
        font_scale (float, optional): Tekstin fontin skaalauskerroin. Oletus 0.8.
        alpha (float, optional): Läpinäkyvyyden aste. Oletus 0.6.

    Returns:
        tuple: Kuva bounding boxien kanssa ja JSON-merkkijono tuloksista.
    """
    # Muunna PIL-kuva numpy-taulukoksi (OpenCV-muoto)
    img = np.array(image)

    # Alusta listat eri objektien bounding boxeille
    port_boxes = []             # Kaikki porttibounding boxit ja niiden tilat
    lan_port_stack_boxes = []   # LAN-porttipinojen bounding boxit
    switch_boxes = []           # Kytkimen bounding boxit

    # Käy läpi kaikki tunnistustulokset
    for result in results:
        # Hae bounding boxit, luottamusarvot ja luokkien ID:t
        boxes = result.boxes.xyxy.cpu().numpy()   # Bounding boxien koordinaatit
        confs = result.boxes.conf.cpu().numpy()   # Luottamusarvot
        classes = result.boxes.cls.cpu().numpy()  # Luokkien ID:t

        # Käy läpi tunnistetut objektit ja tallenna ne vastaaviin listoihin
        for i, box in enumerate(boxes):
            class_id = int(classes[i])  # Objektiluokan ID
            conf = confs[i]             # Luottamusarvo

            if class_id == 0:  # Kaapeli (portti, jossa kaapeli)
                port_boxes.append((box, conf, 'Cable'))
            elif class_id == 1:  # LAN-portti (tyhjä portti)
                port_boxes.append((box, conf, 'empty'))
            elif class_id == 2:  # LAN-porttipino
                lan_port_stack_boxes.append((box, conf))
            elif class_id == 3:  # Kytkin
                switch_boxes.append((box, conf))

    # Luo JSON-tuloste tunnistetuista kytkimistä ja porteista
    json_output_dict = generate_switch_json(lan_port_stack_boxes, port_boxes)

    # Muunna NumPy-tyypit Python-tyypeiksi, jotta ne voidaan serialisoida JSON-muotoon
    json_output_dict = convert_numpy_types(json_output_dict)

    # Serealisoidaan JSON-merkkijonoksi
    json_output = json.dumps(json_output_dict, indent=4)

    # Jälkikäsittely: Säilytä vain portit, joiden keskipiste on jonkin LAN-porttipinon sisällä
    valid_port_boxes = []
    for port_box, conf, status in port_boxes:
        # Tarkista, onko portin keskipiste minkä tahansa LAN-porttipinon sisällä
        is_inside_any_stack = any(
            is_inside(port_box, stack_box) for stack_box, _ in lan_port_stack_boxes
        )
        if is_inside_any_stack:
            valid_port_boxes.append((port_box, conf, status))

    # Piirrä bounding boxit kelvollisille porteille
    for port_box, conf, status in valid_port_boxes:
        # Hae bounding boxin koordinaatit ja muunna kokonaisluvuiksi
        x1, y1, x2, y2 = map(int, port_box)
        if status == 'Cable':
            color = class_colors.get(0, (0, 255, 255))  # Väri kaapelille
            label = f"Kaapeliportti: {conf:.2f}"        # Etiketti kaapeliportille
        else:
            color = class_colors.get(1, (255, 255, 255))  # Väri LAN-portille
            label = f"LAN-portti: {conf:.2f}"             # Etiketti LAN-portille

        # Piirrä suorakulmio (bounding box) portin ympärille
        cv2.rectangle(
            img, (x1, y1), (x2, y2), color=color, thickness=box_thickness
        )

        # Valmistele etiketti luokan nimellä ja luottamusarvolla
        label_size, _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2
        )
        # Määritä etiketin yläreunan sijainti
        y_label_top = (
            y1 - label_size[1] - 10
            if y1 - label_size[1] - 10 > 0
            else y1 + 10
        )
        # Piirrä läpinäkyvä laatikko etiketin taakse
        draw_transparent_box(
            img, x1, y_label_top, x1 + label_size[0], y1,
            color=color, alpha=alpha
        )
        # Kirjoita etiketti kuvaan
        cv2.putText(
            img, label, (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
            (0, 0, 0), 2
        )

    # Piirrä kytkimen bounding boxit (piirretään aina)
    for switch_box, conf in switch_boxes:
        # Hae bounding boxin koordinaatit ja muunna kokonaisluvuiksi
        x1, y1, x2, y2 = map(int, switch_box)
        color = class_colors.get(3, (255, 255, 0))  # Väri kytkimelle
        label = f"Kytkin: {conf:.2f}"               # Etiketti kytkimelle

        # Piirrä suorakulmio kytkimen ympärille
        cv2.rectangle(
            img, (x1, y1), (x2, y2), color=color, thickness=box_thickness
        )

        # Valmistele etiketti
        label_size, _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2
        )
        # Määritä etiketin yläreunan sijainti
        y_label_top = (
            y1 - label_size[1] - 10
            if y1 - label_size[1] - 10 > 0
            else y1 + 10
        )
        # Piirrä läpinäkyvä laatikko etiketin taakse
        draw_transparent_box(
            img, x1, y_label_top, x1 + label_size[0], y1,
            color=color, alpha=alpha
        )
        # Kirjoita etiketti kuvaan
        cv2.putText(
            img, label, (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
            (0, 0, 0), 2
        )

    # Piirrä LAN-porttipinojen bounding boxit (piirretään aina)
    for stack_box, conf in lan_port_stack_boxes:
        # Hae bounding boxin koordinaatit ja muunna kokonaisluvuiksi
        x1, y1, x2, y2 = map(int, stack_box)
        color = class_colors.get(2, (0, 255, 0))  # Väri LAN-porttipinolle
        label = f"LAN-porttipino: {conf:.2f}"     # Etiketti LAN-porttipinolle

        # Piirrä suorakulmio porttipinon ympärille
        cv2.rectangle(
            img, (x1, y1), (x2, y2), color=color, thickness=box_thickness
        )

        # Valmistele etiketti
        label_size, _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2
        )
        # Määritä etiketin yläreunan sijainti
        y_label_top = (
            y1 - label_size[1] - 10
            if y1 - label_size[1] - 10 > 0
            else y1 + 10
        )
        # Piirrä läpinäkyvä laatikko etiketin taakse
        draw_transparent_box(
            img, x1, y_label_top, x1 + label_size[0], y1,
            color=color, alpha=alpha
        )
        # Kirjoita etiketti kuvaan
        cv2.putText(
            img, label, (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
            (0, 0, 0), 2
        )

    # Palauta kuva bounding boxien kanssa ja JSON-tuloste
    return img, json_output
