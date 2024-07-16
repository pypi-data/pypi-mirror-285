from utilmy.viz import vizhtml as vi
from utilmy import pd_read_file

# Load data
data = pd_read_file("train_obesity.csv")
print(data.head())

# Create doc with graphs
doc = vi.htmlDoc(title='Train Obesity')
doc.h2('Train Obesity Data')
doc.h4('plot Data in table format')
doc.table(data,  table_id="test", custom_css_class='intro',use_datatable=True)
doc.hr()

doc.h4('Column plot')

doc.plot_tseries(data, coldate = 'Age', coly1 = ['Height', 'Weight'])
html_code = vi.pd_tseries(data)
