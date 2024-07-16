from utilmy.viz import vizhtml as vi
import pandas as pd

# dataset for garph
df = pd.DataFrame({ 
     'from':['A', 'B', 'C','A'], 
     'to':['D', 'A', 'E','C'], 
     'weight':[1, 2, 1,5]})

# Create doc
doc = vi.htmlDoc(title='Plot Graph',css_name = "A4_size")
doc.h4('Graph Data plot')
doc.table(df, use_datatable=True, table_id="test", 
    custom_css_class='intro')
doc.pd_plot_network(df, cola='from', colb='to', 
    coledge='col_edge',colweight="weight")