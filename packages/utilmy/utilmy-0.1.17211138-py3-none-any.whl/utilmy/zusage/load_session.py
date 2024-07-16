from utilmy import Session
import pandas as pd

# Create session
sess = Session()

# Load Session
sess.load('mysess')
sess.show()

# Print saved dataframe from Session
print(mydf)
