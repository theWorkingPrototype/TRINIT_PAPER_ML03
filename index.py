
import pickle
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd
import json

df=pd.read_csv('Crop_recommendation.csv')
print(df.head())

from sklearn.model_selection import train_test_split

c=df.label.astype('category')
targets = dict(enumerate(c.cat.categories))
open('map.dict', 'w').write(json.dumps(targets))
df['target']=c.cat.codes


y=df.target
X=df[['N','P','K','temperature','humidity','ph','rainfall']]

X_train, X_test, y_train, y_test = train_test_split(X, y,random_state=1)

grad = GradientBoostingClassifier().fit(X_train, y_train)


filename = "local.sav"

pickle.dump(grad, open(filename, 'wb'))
grad = pickle.load(open(filename, 'rb'))

res = grad.score(X_test, y_test)
print(res)

