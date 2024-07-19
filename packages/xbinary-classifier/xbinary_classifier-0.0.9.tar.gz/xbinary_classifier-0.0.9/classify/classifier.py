import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
import numpy as np
class BinaryClassifier:
    
    def __init__(self,X_train,y_train,n_neighbors=4):
        self.X_train = X_train
        self.y_train= y_train
        self.n_neighbors = n_neighbors
        self.knn = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        
    def train(self):
        self.knn.fit(self.X_train, self.y_train)
        
    def predict(self, X_test):
        preds = self.knn.predict(X_test)
        return preds
    
    def evaluate(self, X_test, y_test):
        accuracy = self.knn.score(X_test, y_test)
        print(f'KNN score: {accuracy}\n')
        
        cm = confusion_matrix(y_test, self.predict(X_test))
        
        # Plot confusion matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, cmap='viridis', fmt='d')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        plt.show()
        
        return cm, accuracy
