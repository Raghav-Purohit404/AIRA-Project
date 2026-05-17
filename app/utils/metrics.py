# placeholder
from sklearn.metrics import accuracy_score


class Metrics:

    @staticmethod
    def calculate_accuracy(y_true, y_pred):
        return accuracy_score(y_true, y_pred)