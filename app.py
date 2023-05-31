import gradio as gr
from missions import operators, check_miss
from article import article, description

mission_names = [
        'Basic Mission', 'Bayonet', 'Breach', 'BSS', 'Cleanup', 'Common Only',
        'Cover', 'Hammer', 'HILDR', 'Knife', 'Locals', 'Logistics',
        'Rare Only', 'Recon', 'Showdown', 'Uncommon Only'
    ]

def process_missions(mission_list, x):
    # Elabora le missioni e restituisci i risultati come stringa multi-linea
    output_list = []
    output_list.append('')

    missioni_migliori = check_miss(operators, mission_list, x)
    new_dict = {}

    for key, value in missioni_migliori.items():
        if value in new_dict:
            new_dict[value].append(key)
        else:
            new_dict[value] = [key]

    for i, key in enumerate(mission_list):
        if key in new_dict:
            output_list.append(f'Mission {i + 1} {mission_list[i]} --> {", ".join(new_dict[key])}')
        else:
            output_list.append(f'Mission {i + 1} {mission_list[i]} -->')

    output_list.append('-----------------------')
    output_list.append('Operator Repositioning')

    check_dict = {}
    for i in range(x, len(mission_list)):
        miss_list = []
        op_list = []
        tmp_dict = check_miss(operators, mission_list[i:])

        for key in tmp_dict:
            if key in check_dict:
                if tmp_dict[key] == check_dict[key]:
                    continue
                else:
                    miss_list.append(tmp_dict[key])
                    op_list.append(key)
        check_dict = tmp_dict

        # unisco le due liste in un dizionario
        no_miss_dict = dict(zip(op_list, miss_list))

        result = ""
        for value in set(no_miss_dict.values()):
            keys = [k for k, v in no_miss_dict.items() if v == value]
            if len(keys) > 1:
                result += ", ".join(keys) + " ({})".format(value) + ", "
            else:
                result += keys[0] + " ({})".format(value) + ", "

        if i != x:
            output_list.append(f'After mission {i} --> {result[:-2]}')

    return "\n".join(output_list)

iface = gr.Interface(
    fn=process_missions, 
    inputs=[
        gr.inputs.CheckboxGroup(choices=mission_names, label='Missions'), 
        gr.inputs.Slider(minimum=0, maximum=3, step=1, default=0, label='Empty missions')
    ], 
    outputs='text',
    title='Tacticool Operators Positioning',
    description=description,
    article=article,
    theme=gr.themes.Default()
)
iface.launch()