from helpers import is_inside, get_center
import numpy as np

def generate_switch_json(lan_port_stack_boxes, port_boxes):
    """
    Generoi JSON-muotoisen rakenteen kytkimille, LAN-porttistackeille ja porteille.

    Parametrit:
        lan_port_stack_boxes (lista): Lista LAN-porttistackien koordinaattilaatikoista.
        port_boxes (lista): Lista porttien koordinaattilaatikoista ja niiden statuksista.

    Palauttaa:
        dict: Sanakirja, joka sisältää kytkimien, porttistackien ja porttien tiedot.
    """
    # Alustetaan tulossanakirja, joka sisältää kytkimet
    output = {
        "switches": []
    }

    # Tarkistetaan, onko yhtään LAN-porttistackia
    if len(lan_port_stack_boxes) == 0:
        print("Ei tunnistettuja LAN-porttistackeja.")
        return output  # Palautetaan tyhjä sanakirja, jos stackeja ei löydy

    # Järjestetään stackit pystysuoran sijainnin (y1-koordinaatin) mukaan
    lan_port_stack_boxes = sorted(
        lan_port_stack_boxes,
        key=lambda box: box[0][1]  # Järjestä y1-koordinaatin perusteella
    )

    # Alustetaan muuttujat kytkimien käsittelyä varten
    current_switch_id = 1  # Nykyisen kytkimen ID
    current_switch_start = int(lan_port_stack_boxes[0][0][1])  # Nykyisen kytkimen aloituskohta
    switch_threshold = 500  # Kynnysarvo pystysuoralle etäisyydelle stackien välillä

    # Alustetaan nykyisen kytkimen tiedot
    switch_data = {
        "switch_id": f"Switch_{current_switch_id}",
        "lan_port_stacks": []
    }

    stack_counter = 1  # Stackien laskuri
    base_port_number = 1  # Porttien numerointi alkaa tästä

    # Käydään läpi jokainen LAN-porttistack
    for stack_box, _ in lan_port_stack_boxes:
        stack_box_y = int(stack_box[1])  # Stackin y1-koordinaatti

        # Tarkistetaan, tulisiko aloittaa uusi kytkin
        if stack_box_y > current_switch_start + switch_threshold:
            # Tallennetaan nykyisen kytkimen tiedot
            output["switches"].append(switch_data)

            # Aloitetaan uusi kytkin
            current_switch_id += 1
            switch_data = {
                "switch_id": f"Switch_{current_switch_id}",
                "lan_port_stacks": []
            }
            current_switch_start = stack_box_y  # Päivitetään kytkimen aloituskohta
            base_port_number = 1  # Nollataan porttinumero uudelle kytkimelle

        # Etsitään portit, jotka sijaitsevat tässä stackissa
        ports_in_stack = [
            (port_box, status)
            for port_box, _, status in port_boxes
            if is_inside(port_box, stack_box)
        ]

        # Jos portteja ei löydy, siirrytään seuraavaan stackiin
        if not ports_in_stack:
            continue

        # Lasketaan kunkin portin keskipisteen koordinaatit
        port_centers = [
            (get_center(port_box), status)
            for port_box, status in ports_in_stack
        ]

        # Järjestetään portit x-koordinaatin mukaan (vasemmalta oikealle)
        port_centers = sorted(port_centers, key=lambda x: x[0][0])  # x-koordinaatti

        # Debug: Tulostetaan järjestetyt portit x-koordinaatin mukaan
        print(f"\nStack {stack_counter}: Portit järjestetty x-koordinaatin mukaan:")
        for center, status in port_centers:
            print(f"Portin keskipiste x: {center[0]:.2f}, y: {center[1]:.2f}, status: {status}")

        # Alustetaan listat ylemmille ja alemmille porteille
        upper_ports = []
        lower_ports = []

        # Ryhmitellään portit sarakkeisiin x-koordinaatin läheisyyden perusteella
        x_coords = [center[0][0] for center in port_centers]
        x_diffs = np.diff(x_coords)
        avg_x_diff = np.mean(x_diffs) if len(x_diffs) > 0 else 0
        threshold = avg_x_diff * 0.5 if avg_x_diff > 0 else 10  # Tai kiinteä arvo

        columns = []
        current_column = [port_centers[0]]

        # Ryhmitellään portit sarakkeisiin
        for i in range(1, len(port_centers)):
            if x_coords[i] - x_coords[i-1] <= threshold:
                # Sama sarake
                current_column.append(port_centers[i])
            else:
                # Uusi sarake
                columns.append(current_column)
                current_column = [port_centers[i]]
        columns.append(current_column)

        # Debug: Tulostetaan sarakkeet
        print(f"\nStack {stack_counter}: Sarakkeet ryhmittelyn jälkeen:")
        for idx, column in enumerate(columns):
            print(f"Sarake {idx + 1}:")
            for center, status in column:
                print(f"  Portin keskipiste x: {center[0]:.2f}, y: {center[1]:.2f}, status: {status}")

        # Käsitellään jokainen sarake porttinumeroiden antamiseksi
        for column in columns:
            # Järjestetään portit sarakkeessa y-koordinaatin mukaan
            column = sorted(column, key=lambda x: x[0][1])  # y-koordinaatti

            if len(column) >= 2:
                # Ylempi portti (pienempi y-koordinaatti)
                upper_port = column[0]
                upper_port_data = {
                    "port_number": base_port_number,  # Pariton numero
                    "status": upper_port[1]
                }
                upper_ports.append(upper_port_data)

                # Alempi portti (suurempi y-koordinaatti)
                lower_port = column[1]
                lower_port_data = {
                    "port_number": base_port_number + 1,  # Parillinen numero
                    "status": lower_port[1]
                }
                lower_ports.append(lower_port_data)

                # Debug: Tulostetaan annetut porttinumerot
                print(f"\nAnnetut porttinumerot sarakkeelle, joka alkaa x = {column[0][0][0]:.2f}:")
                print(f"  Ylempi porttinumero: {upper_port_data['port_number']}, status: {upper_port_data['status']}")
                print(f"  Alempi porttinumero: {lower_port_data['port_number']}, status: {lower_port_data['status']}")

            elif len(column) == 1:
                # Vain yksi portti sarakkeessa
                port = column[0]
                lower_port_data = {
                    "port_number": base_port_number + 1,  # Parillinen numero
                    "status": port[1]
                }
                lower_ports.append(lower_port_data)

                # Debug: Tulostetaan annettu porttinumero
                print(f"\nAnnettu porttinumero yksittäiselle portille x = {port[0][0]:.2f}:")
                print(f"  Porttinumero: {lower_port_data['port_number']}, status: {lower_port_data['status']}")

            # Kasvatetaan perusporttinumeroa seuraavaa saraketta varten
            base_port_number += 2

        # Järjestetään portit kussakin rivissä porttinumeron mukaan
        upper_ports = sorted(upper_ports, key=lambda x: x["port_number"])
        lower_ports = sorted(lower_ports, key=lambda x: x["port_number"])

        # Debug: Tulostetaan ylemmät ja alemmat portit ennen lisäämistä stack_dataan
        print(f"\nStack {stack_counter}: Ylemmät portit:")
        for port in upper_ports:
            print(f"  Porttinumero: {port['port_number']}, status: {port['status']}")
        print(f"Stack {stack_counter}: Alemmat portit:")
        for port in lower_ports:
            print(f"  Porttinumero: {port['port_number']}, status: {port['status']}")

        # Luodaan sanakirja tälle stackille
        stack_data = {
            "stack_id": f"Stack_{stack_counter}",
            "lan_ports": [upper_ports, lower_ports]  # Ylemmät portit ensin
        }

        # Lisätään stackin tiedot nykyiseen kytkimeen
        switch_data["lan_port_stacks"].append(stack_data)

        # Kasvatetaan stackien laskuria
        stack_counter += 1

    # Lisätään viimeisen kytkimen tiedot tulokseen
    output["switches"].append(switch_data)

    # Palautetaan tulossanakirja
    return output
