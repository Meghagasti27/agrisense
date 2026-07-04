from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


FEATURES = [
    "Crop",
    "Crop_Year",
    "Season",
    "State",
    "Area",
    "Annual_Rainfall",
    "Fertilizer",
    "Pesticide",
]

CATEGORICAL_FEATURES = ["Crop", "Season", "State"]
NUMERIC_FEATURES = [
    "Crop_Year",
    "Area",
    "Annual_Rainfall",
    "Fertilizer",
    "Pesticide",
]

# Approximate relative farmgate prices. These are intentionally conservative
# placeholders so ranking is not a raw "yield * 10" calculation.
CROP_PRICES_INR = {
    "Arecanut": 280,
    "Arhar/Tur": 95,
    "Bajra": 25,
    "Banana": 15,
    "Barley": 22,
    "Black pepper": 500,
    "Cardamom": 1200,
    "Cashewnut": 110,
    "Castor seed": 55,
    "Coconut": 12,
    "Coriander": 80,
    "Cotton(lint)": 65,
    "Dry chillies": 160,
    "Garlic": 80,
    "Ginger": 60,
    "Gram": 60,
    "Groundnut": 65,
    "Jowar": 30,
    "Jute": 45,
    "Linseed": 60,
    "Maize": 22,
    "Mesta": 40,
    "Moong(Green Gram)": 85,
    "Onion": 18,
    "Potato": 18,
    "Ragi": 38,
    "Rapeseed &Mustard": 58,
    "Rice": 22,
    "Safflower": 55,
    "Sesamum": 120,
    "Small millets": 35,
    "Soyabean": 45,
    "Sugarcane": 3,
    "Sunflower": 60,
    "Sweet potato": 20,
    "Tapioca": 8,
    "Tobacco": 160,
    "Turmeric": 90,
    "Urad": 80,
    "Wheat": 24,
}


class CropYieldPredictorV2:
    def __init__(self):
        self.crops: list[str] = []
        self.model = None
        self.model_metrics = {}
        self.crop_stats: dict[str, dict[str, float]] = {}
        self.data_file = Path(__file__).parent / "data" / "crop_yield.csv"
        self.model_dir = Path(__file__).parent / "models"
        self.model_dir.mkdir(exist_ok=True)
        self.model_file = self.model_dir / "crop_yield_v3.joblib"

        self.df = self._load_dataset()
        self.crops = sorted(self.df["Crop"].unique())
        self._build_crop_stats()

        if not self._load_model():
            self._train_model()

    def _load_dataset(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_file)
        for column in CATEGORICAL_FEATURES:
            df[column] = df[column].astype(str).str.strip()
        return df

    def _build_crop_stats(self) -> None:
        grouped = self.df.groupby("Crop")["Yield"]
        stats = grouped.agg(["median", "mean", "std"]).fillna(0)

        self.crop_stats = {
            crop: {
                "median": max(float(row["median"]), 0.01),
                "mean": max(float(row["mean"]), 0.01),
                "std": max(float(row["std"]), 0.0),
            }
            for crop, row in stats.iterrows()
        }

    def _load_model(self) -> bool:
        if not self.model_file.exists():
            return False

        try:
            bundle = joblib.load(self.model_file)
            self.model = bundle["model"]
            self.model_metrics = bundle.get("metrics", {})
            return True
        except Exception as exc:
            print(f"Could not load saved crop model; retraining: {exc}")
            return False

    def _train_model(self) -> None:
        X = self.df[FEATURES]
        y = self.df["Yield"].clip(lower=0)

        preprocessor = ColumnTransformer(
            [
                ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
                ("num", "passthrough", NUMERIC_FEATURES),
            ]
        )

        self.model = Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "rf",
                    RandomForestRegressor(
                        n_estimators=160,
                        min_samples_leaf=2,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
        )

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        self.model_metrics = {
            "r2_score": round(float(r2_score(y_test, predictions)), 3),
            "training_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
        }
        print("CropYieldPredictorV2 metrics:", self.model_metrics)

        joblib.dump(
            {
                "model": self.model,
                "metrics": self.model_metrics,
            },
            self.model_file,
        )

    def get_all_crops(self) -> list[str]:
        return self.crops

    def get_candidate_crops(self, season: str, state: str) -> list[str]:
        season = season.strip()
        state = state.strip()
        candidates = self.df[
            (self.df["Season"] == season) &
            (self.df["State"] == state)
        ]["Crop"].unique()

        if len(candidates) > 0:
            return sorted(candidates)

        state_candidates = self.df[self.df["State"] == state]["Crop"].unique()
        if len(state_candidates) > 0:
            return sorted(state_candidates)

        return self.get_all_crops()

    def _confidence_from_trees(self, mean_pred: float, std_pred: float) -> float:
        if mean_pred <= 0:
            return 0.0

        uncertainty_ratio = std_pred / (abs(mean_pred) + std_pred)
        return max(0.0, min(100.0, 100.0 * (1.0 - uncertainty_ratio)))

    def _yield_index(self, crop: str, predicted_yield: float) -> float:
        median = self.crop_stats.get(crop, {}).get("median", 1.0)
        return max(0.0, min(predicted_yield / median, 3.0))

    def _price_for_crop(self, crop: str) -> float:
        return CROP_PRICES_INR.get(crop, 20.0)

    def predict_crop_yield(
        self,
        crop: str,
        crop_year: int,
        season: str,
        state: str,
        area: float,
        rainfall: float,
        fertilizer: float,
        pesticide: float,
    ) -> dict:
        row = pd.DataFrame(
            [
                {
                    "Crop": crop.strip(),
                    "Crop_Year": crop_year,
                    "Season": season.strip(),
                    "State": state.strip(),
                    "Area": area,
                    "Annual_Rainfall": rainfall,
                    "Fertilizer": fertilizer,
                    "Pesticide": pesticide,
                }
            ]
        )

        prediction = max(float(self.model.predict(row)[0]), 0.0)
        rf = self.model.named_steps["rf"]
        transformed_row = self.model.named_steps["preprocessor"].transform(row)
        tree_predictions = np.array(
            [max(float(tree.predict(transformed_row)[0]), 0.0) for tree in rf.estimators_]
        )

        mean_pred = max(float(np.mean(tree_predictions)), 0.0)
        std_pred = max(float(np.std(tree_predictions)), 0.0)
        confidence = self._confidence_from_trees(mean_pred, std_pred)
        yield_index = self._yield_index(crop, prediction)
        estimated_profit = prediction * self._price_for_crop(crop)

        # Rank by crop-relative yield first, then confidence and profit. This avoids
        # crops with naturally large yield units always dominating the recommendation.
        recommendation_score = (yield_index * 70.0) + (confidence * 0.25) + min(estimated_profit / 10000.0, 10.0)

        return {
            "yield": round(prediction, 2),
            "confidence": round(confidence, 2),
            "min_yield": round(max(mean_pred - std_pred, 0.0), 2),
            "max_yield": round(mean_pred + std_pred, 2),
            "estimated_profit": round(estimated_profit, 2),
            "yield_index": round(yield_index, 2),
            "recommendation_score": round(recommendation_score, 2),
        }

    def get_model_info(self) -> dict:
        return {
            "model_type": "RandomForestRegressor crop yield recommender",
            "metrics": self.model_metrics,
            "features": FEATURES,
            "crops": self.crops,
            "ranking_note": "Recommendations are filtered by state/season and ranked by crop-relative yield, confidence, and estimated profit.",
        }


CropYieldPredictor = CropYieldPredictorV2
_predictor = None


def get_predictor() -> CropYieldPredictorV2:
    global _predictor

    if _predictor is None:
        _predictor = CropYieldPredictorV2()

    return _predictor


def predict_yield(features: dict) -> dict:
    predictor = get_predictor()

    return predictor.predict_crop_yield(
        crop=features["Crop"],
        crop_year=features["Crop_Year"],
        season=features["Season"],
        state=features["State"],
        area=features["Area"],
        rainfall=features["Annual_Rainfall"],
        fertilizer=features["Fertilizer"],
        pesticide=features["Pesticide"],
    )
