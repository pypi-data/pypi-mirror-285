from utilmy.viz import vizhtml as vi

data = vi.test_getdata()
df = data['stock_data.csv']
html_code = vi.pd_plot_tseries_highcharts(df,
                                            coldate='Date',
                                            date_format='%m%d%Y',
                                            cols_axe1=['Open'],
                                            cols_axe2=['Colse'],
                                            title='Stock Data',
                                            x_label='Date',
                                            axe1_label='Axe 1 Label',
                                            axe2_lael='Axe 2 Label')
vi.html_show_charthighchart(html_code)