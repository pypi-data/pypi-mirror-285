import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
import numpy as np
class binaryclassify:
    
    def __init__(self,X,y,n_neighbors=4):
        self.X = X
        self.y = y
        self.n_neighbors = n_neighbors
        self.knn = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        
    def predict(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, random_state=0)
        
        
        KNN_fit=self.knn.fit(X_train, y_train)
        accuracy = self.knn.score(X_test, y_test)
        
        print(f'KNN score: {accuracy}\n')
        
        cv_scores = cross_val_score(self.knn, self.X, self.y, cv=3)
        print('Cross-validation scores (3-fold):', cv_scores)
        print('Mean cross-validation score (3-fold): {:.3f}'.format(np.mean(cv_scores)))
        preds = KNN_fit.predict(X_test)
        cm = confusion_matrix(y_test, preds)
        sns.heatmap(cm, annot=True, cmap='viridis')
        return preds
