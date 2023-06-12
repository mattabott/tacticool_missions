import gradio as gr
from missions import operators, check_miss
from article import article, description
import matplotlib.pyplot as plt
from PIL import Image
import io

mission_names = [
        'Basic Mission', 'Bayonet', 'Breach', 'BSS', 'Cleanup', 'Common Only',
        'Cover', 'Hammer', 'HILDR', 'Knife', 'Locals', 'Logistics',
        'Rare Only', 'Recon', 'Showdown', 'Uncommon Only'
    ]

def process_missions(mission_list, x):
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

        no_miss_dict = dict(zip(op_list, miss_list))

        result = ""
        for value in set(no_miss_dict.values()):
            keys = [k for k, v in no_miss_dict.items() if v == value]
            if len(keys) > 1:
                result += ", ".join(keys) + " ({})".format(value) + ", "
            else:
                result += keys[0] + " ({})".format(value) + ", "

        if i == 0:
            continue
        else:
            output_list.append(f'After mission {i} --> {result[:-2]}')


    height = len(output_list) * 0.5

    fig, ax = plt.subplots(figsize=[10, height])

    ax.axis('off')

    text = '\n'.join(output_list)
    ax.text(0.02, 0.90, text, fontsize=12, va='top', ha='left')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.2, dpi=300)
    buf.seek(0)
    img = Image.open(buf)

    plt.close()

    return img

iface = gr.Interface(
    fn=process_missions, 
    inputs=[
        gr.inputs.CheckboxGroup(choices=mission_names, label='Missions'), 
        gr.inputs.Slider(minimum=0, maximum=3, step=1, default=0, label='Empty missions')
    ], 
    outputs=gr.outputs.Image(type='pil'),
    title='Tacticool Operators Positioning',
    description=description,
    article=article,
    theme=gr.themes.Default()
)
iface.launch()