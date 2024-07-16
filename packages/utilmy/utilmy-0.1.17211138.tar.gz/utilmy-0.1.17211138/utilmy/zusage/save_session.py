from utilmy import Session
import pandas as pd

# Create session
sess = Session("ztmp/session")

# Load .csv into pandas DataFrame
mydf = pd.read_csv('train_obesity.csv')
another_df = pd.DataFrame([1], columns=['a'] )

print(mydf)

# Save session
sess.save('mysess', globals())
sess.show()
