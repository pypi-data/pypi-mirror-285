#%%
import altair as alt
import pandas as pd
from ipywidgets import HBox, VBox, HTML

def filter_box(callback, 
                  label_width=50, 
                  bar_width=300, 
                  bar_height=20,
                  **kwargs0):

    kwargs = {}
    for k in kwargs0:
        if isinstance(kwargs0[k], list):
            nv = {'values': kwargs0[k]}
        else:
            nv = kwargs0[k]

        kwargs[k] = nv
    
    global_selection = {}
    def on_select(change):
        sel = change.new.value
        if 'a' in sel:
            # print(kwargs[change.name])
            global_selection[change.name] = [kwargs[change.name]['values'][x] for x in sel['a']] 
        else:
            if change.name in global_selection:
                del global_selection[change.name]
        callback(global_selection)

    def new_bar(name, values, selection=None, color='red'):
        if selection is None:
            brush = alt.selection_interval( name=name, encodings=['x'], empty=False)
        elif len(selection) == 1:
            selection_ids = [values.index(x) for x in selection]
            brush = alt.selection_interval( name=name, encodings=['x'], value=selection_ids[0], empty=False)
            global_selection[name] = selection
        elif len(selection) == 2:
            selection_ids = [values.index(x) for x in selection]
            brush = alt.selection_interval( name=name, encodings=['x'], value={'x': selection_ids}, empty=False)
            global_selection[name] = selection
        else:
            brush = alt.selection_interval( name=name, encodings=['x'], empty=False)

        ids = [x for x in range(len(values))]
        base = alt.Chart(pd.DataFrame({'a':ids, 'txt':values})).encode(
            x='a:O',
        )

        chart = base.mark_rect(
            cornerRadius=0
        ).encode(
            color=alt.condition(brush, alt.value(color), alt.value('lightgray'))
        ).add_params(brush)

        text = base.mark_text(baseline="middle").encode(
            text="txt",
        )

        out  = chart + text

        out2 = out.properties(
            width=bar_width,
            height=bar_height,
        ).configure_view(
            stroke=None,
        ).configure_axis(
            grid=False,
            tickSize=0,
            labels=False,
            title='',
            domainWidth=0
        ).configure_legend(
            disable=True,
        )

        chart_widget = alt.JupyterChart(out2, 
                                        embed_options={'actions':False},
                                        debounce_wait=1000)

        chart_widget.selections.observe(on_select, [name])
        return chart_widget
    
    arr = []
    for x in kwargs:
        v = kwargs[x]
        if isinstance(v, list):
            v = {'values':v}
        print(v)
        bar = new_bar(x, **v)
        arr.append(HBox([HTML(f'<div style="width: {label_width}px">{x}</div>'), bar]))

    return VBox(arr) 

filter_box(lambda x:print(x),  
              x={'values':[1,2,3,4,5,6,7], 'selection':[4]},
              y=[3,4,5]
              )
