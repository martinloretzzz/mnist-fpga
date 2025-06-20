import xgboost as xgb
from util import get_mnist_dataset

x_train, y_train = get_mnist_dataset(train=True, as_np_array=True)
x_test, y_test = get_mnist_dataset(train=False, as_np_array=True)

model = xgb.XGBClassifier(
    learning_rate=0.5,
    n_estimators=100,
    tree_method="hist",
    objective="multi:softmax",
    num_class=10,
    max_depth=4,
    subsample=0.8,
    min_child_weight=3,
    reg_lambda=1.0,
    reg_alpha=0.1,
    random_state=42
)

model.fit(x_train, y_train)
y_pred = model.predict(x_test)

accuracy = (y_pred == y_test).sum().item() / len(y_test)
print(f"Test Accuracy: {accuracy:.4f}")

booster = model.get_booster()
booster.dump_model("model.json", dump_format="json")
booster_dump = booster.get_dump()
params = model.get_params()
