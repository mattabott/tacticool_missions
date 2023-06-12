from supremacy1914_wrapper import Supremacy, ServerChangeError
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import gradio as gr
import io
import re
import pandas as pd
import json
from PIL import Image
from description import description, article

def split_and_strip(input_string): 
    split_string = input_string.split(',')

    stripped_string = [s.strip() for s in split_string]
    
    return stripped_string

def find_player(game_id):
    supremacy = Supremacy(game_id, 'http://xgs-rc2.c.bytro.com')

    try:
        players = supremacy.players()
    except ServerChangeError as exception:
        supremacy.url = str(exception)
        players = supremacy.players()
    
    player_name_list = []
    player_id_list = []
    player_nation_name_list = []

    for key, value in players['players'].items():
        player_name_list.append(value['name'])
        player_id_list.append(value['playerID'])
        player_nation_name_list.append(value['nationName'])

    return player_id_list, player_name_list, player_nation_name_list
    
def check_players(game_id, pl): 
    pl_id, pl_name, pl_nation_name = find_player(game_id)

    pl_list = split_and_strip(pl)
    name_list = []
    id_list = []
    nation_list = []

    for name in pl_list:
        if name in pl_name:
            name_list.append(name)
            index = pl_name.index(name)  
            id_list.append(pl_id[index]) 
            nation_list.append(pl_nation_name[index]) 
        else:
            continue
    return name_list, id_list, nation_list

def regions(day, player_id):
    tot_prov = 0
    try:
        score_day = supremacy.score(day)

        for key, value in score_day['mapInfo'].items():
            if key == 'owner':
                for i in score_day['mapInfo'][key]:
                    if i == player_id:
                        tot_prov += 1
    except:
        tot_prov = 0

    return tot_prov

def sup_score(day, player_id):
    score_day = supremacy.score(day)

    player_score = score_day['ranking']['ranking'][player_id]

    return player_score

def lst_region(day, player_id):
    reg_list = []

    for i in range(day):
        score = regions(i, player_id)
        reg_list.append(score)

    return reg_list

def pl_points(day, player_id):
    app_list = []

    for i in range(day):
        app_list.append(sup_score(i, player_id))

    return app_list



#Funzione per cercare nel giornale se esiste il nome della nazione e prendere solo i dati relativi alle perdite
def check_in_journal(nation_name, input_string):
    # Usa l'espressione regolare per trovare la cifra associata a 'Stati del Pacifico'
    match = re.search(fr"\{{{{countryLink '{nation_name}' .*?}}}} - ([\d,]+)", input_string)

    # Se l'espressione regolare ha trovato una corrispondenza, stampala
    if match:
        death_str = match.group(1)
        death = int(death_str.replace(',', '')) # Converti la stringa in un numero
        return death

    return 0 # Ritorna 0 se non c'è corrispondenza


#funzione per calcolare le morti dei players
def calculate_points_per_player(id_list, name_list, days, players, check_in_journal):
    # Creiamo un dizionario che mappa gli ID ai nomi
    id_to_name = {str(id): name for id, name in zip(id_list, name_list)}

    # Inizializziamo il dizionario points_per_player con i nomi invece degli ID
    points_per_player = {name: [0]*days for name in name_list}

    for i in range(1, days):
        try:
            response = supremacy.score(i)
            articles = response['articles']
        except json.JSONDecodeError:
            print(f"Errore nell'elaborazione della risposta per il giorno {i}")
            continue

        for article in articles:
            for key, value in article.items():
                if key == 'messageBody':
                    for player_id in id_to_name.keys():
                        nationName = players['players'][player_id]['nationName']
                        player_name = id_to_name[player_id]
                        points_per_player[player_name][i-1] += check_in_journal(nationName, value)
    return points_per_player

def dead_graphic(points_per_player, day):
    # Crea un DataFrame da points_per_player
    df = pd.DataFrame(points_per_player)

    # Aggiunge 1 all'indice per fare in modo che i giorni inizino da 1
    df.index = df.index + 1

    # Trasforma il DataFrame in formato lungo
    df = df.reset_index().melt(id_vars='index', var_name='Player', value_name='Dead')
    df = df.rename(columns={'index': 'Day'})

    # Crea un barplot
    plt.figure(figsize=(day, day/2))
    sns.barplot(x='Day', y='Dead', hue='Player', data=df)
    plt.title('Dead per Day')
    plt.grid()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)

    plt.close()

    return image


def check_dead(game_id, pl_list, days, players):
    name_list, id_list, nation_list = check_players(game_id, pl_list)
    points_per_player = calculate_points_per_player(id_list,name_list, days, players, check_in_journal)
    return dead_graphic(points_per_player, days)


def graphic(dictionary, day):
    plt.figure(figsize=(day, day/2))

    colors = plt.cm.rainbow(np.linspace(0, 1, len(dictionary)))

    legend_elements = []

    for color, (name, data) in zip(colors, dictionary.items()):
        points = data['points']
        regions = data['regions']

        legend_elements.append(plt.Line2D([0], [0], color=color, lw=4, label=name))

        sns.lineplot(x=list(range(len(points)+1))[1:], y=points, color=color)

        for i in range(len(regions)):
            plt.text(x=i+1, y=points[i+1], s=regions[i], ha='center', color=color)

    plt.xticks(list(range(len(points)+1))[1:])

    plt.legend(handles=legend_elements, loc='upper left')
    plt.title('Points / Regions per Day')
    plt.grid()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)

    plt.close()

    return image


def not_main(id_game, day, input_players):

    day = int(day)
    global supremacy
    supremacy = Supremacy(id_game, 'http://xgs-rc2.c.bytro.com')
    try:
        players = supremacy.players()
        
    except ServerChangeError as exception:
        supremacy.url = str(exception)
        supremacy = Supremacy(id_game, supremacy.url)
        players = supremacy.players()


    pl_name, pl_id, _ = check_players(id_game, input_players)

    dictionary = {}

    for name, id in zip(pl_name, pl_id):
        points = pl_points(day, id)
        pl_regions = lst_region(day-1, id)
        dictionary[name] = {'points': points, 'regions': pl_regions}
    
    return graphic(dictionary, day), check_dead(id_game, input_players, day, players)



iface = gr.Interface(
    fn=not_main, 
    inputs=[
        gr.inputs.Textbox(label='Game ID'),
        gr.inputs.Number(label='Day'),
        gr.inputs.Textbox(label='Players name')
    ], 
    outputs=[
        gr.outputs.Image(type='pil'),
        gr.outputs.Image(type='pil')
        ],
    title='Supremacy Analysis',
    description=description,
    article=article,
    
)

iface.launch()