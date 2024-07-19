from functools import partial

import numpy as np
import optuna
import pandas as pd
import skops.io as sio
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm
from tsfresh import extract_features

from flarespy.utils import FC_PARAMETERS

from .utils import PACKAGEDIR

# Define the search space
SEARCH_SPACE = {
    "n_estimators": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    "max_depth": [3, 5, 7, 9, 11, 13, 15, 17],
    "max_features": [2, 3, 4, 5],
}


class SimData:
    def __init__(self, sim_path):
        training_data, self.training_y = load_simulation("training", sim_path=sim_path)
        self.training_x = extract_features(
            training_data,
            column_id="id",
            column_sort="time",
            default_fc_parameters=FC_PARAMETERS,
        )

        validation_data, self.validation_y = load_simulation("validation", sim_path=sim_path)
        self.validation_x = extract_features(
            validation_data,
            column_id="id",
            column_sort="time",
            default_fc_parameters=FC_PARAMETERS,
        )

        test_data, self.test_y = load_simulation("test", sim_path=sim_path)
        self.test_x = extract_features(
            test_data,
            column_id="id",
            column_sort="time",
            default_fc_parameters=FC_PARAMETERS,
        )


def load_simulation(set_type, sim_path):
    data = pd.DataFrame(columns=["id", "time", "flux"], dtype=float)
    target = pd.Series(dtype=int)

    sim_id_start = 0
    type_id = 0
    for sim_type in ["flare", "non-flare"]:
        sim_file_path = str(sim_path / "{}-{}.npz".format(set_type, sim_type))
        sim_file = np.load(sim_file_path)

        n_simulation = len(sim_file.files)
        target = pd.concat([target, pd.Series(np.ones(n_simulation, dtype=int) * type_id)])

        for i in tqdm(range(n_simulation), desc="Loading {}".format(sim_type)):
            sim_data = sim_file["arr_" + str(i)]
            sim_id = np.ones(sim_data.shape[0], dtype=int) * i + sim_id_start
            sim_df = pd.DataFrame({"id": sim_id, "time": sim_data[:, 0], "flux": sim_data[:, 1]})
            data = pd.concat([data, sim_df])

        sim_id_start += n_simulation
        type_id += 1

    return data, target.reset_index(drop=True)


# Define the objective function
def objective(trial, sim_data):
    n_estimators = trial.suggest_categorical("n_estimators", SEARCH_SPACE["n_estimators"])
    max_depth = trial.suggest_categorical("max_depth", SEARCH_SPACE["max_depth"])
    max_features = trial.suggest_categorical("max_features", SEARCH_SPACE["max_features"])

    classifier = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth, max_features=max_features, random_state=0
    )

    # Train the model on the training set
    classifier.fit(sim_data.training_x, sim_data.training_y)

    # Evaluate the model on the validation set
    y = classifier.predict(sim_data.validation_x)
    score = accuracy_score(sim_data.validation_y, y)

    return score


def train_model(
    search_space=None,
    sim_path=PACKAGEDIR / "data" / "simulation",
    model_path=PACKAGEDIR / "data",
    model_filename="model.dat",
):
    if search_space is None:
        search_space = SEARCH_SPACE
    model_path.mkdir(exist_ok=True)

    sim_data = SimData(sim_path=sim_path)
    objective_with_params = partial(objective, sim_data=sim_data)

    # Create a study object and perform grid search
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.GridSampler(search_space, seed=0))
    study.optimize(objective_with_params, n_trials=None)  # Set n_trials=None to search all combinations

    # Print the best hyperparameters
    print("Best trial:")
    trial = study.best_trial

    print("  Value: {}".format(trial.value))
    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))

    rfc = RandomForestClassifier(
        n_estimators=trial.params["n_estimators"],
        max_depth=trial.params["max_depth"],
        max_features=trial.params["max_features"],
        random_state=0,
    )

    rfc.fit(sim_data.training_x, sim_data.training_y)
    sio.dump(rfc, model_path / model_filename)

    importance_frame = pd.DataFrame(
        {
            "mean": rfc.feature_importances_,
            "std": np.std([tree.feature_importances_ for tree in rfc.estimators_], axis=0),
        },
        index=sim_data.training_x.columns.values,
    )
    importance_frame.index.name = "feature"

    importance_frame.sort_values(by=["mean"], ascending=False).to_csv(model_path / "importance.csv")

    score = f1_score(sim_data.test_y, rfc.predict(sim_data.test_x))
    print(f"F1 score: {score:.3f}")
