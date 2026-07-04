// // TypeScript types for AgriSense ML API

// export interface CropInput {
//   soil_type: 'Loamy' | 'Sandy' | 'Clayey' | 'Alluvial';
//   pH: number;
//   rainfall_30: number;
//   avg_temp_30: number;
//   lat: number;
//   lon: number;
//   irrigation: boolean;
// }

// export interface CropRecommendation {
//   crop: string;
//   estimated_yield_kg_per_acre: number;
//   estimated_profit_inr_per_acre: number;
//   risk: string;
//   confidence?: number;
//   min_yield?: number;
//   max_yield?: number;
// }

// export interface RecommendResponse {
//   recommendations: CropRecommendation[];
// }

// export interface ModelMetrics {
//   r2_mean: number;
//   r2_std: number;
//   n_samples: number;
//   n_features: number;
// }

// export interface FeatureImportance {
//   soil_type: number;
//   pH: number;
//   rainfall_mm: number;
//   temperature_C: number;
//   latitude: number;
//   irrigation: number;
// }

// export interface ModelInfo {
//   model_type: string;
//   n_estimators: number;
//   training_samples: number;
//   soil_types: string[];
//   features: string[];
//   metrics: ModelMetrics;
//   feature_importance: FeatureImportance;
// }

// export interface ApiError {
//   detail: string;
// }
// TypeScript types for AgriSense ML API

export interface CropInput {
  crop_year: number;
  season: string;
  state: string;
  area: number;
  annual_rainfall: number;
  fertilizer: number;
  pesticide: number;
}

export interface CropRecommendation {
  crop: string;
  estimated_yield: number;
  estimated_profit: number;
  rank: number;
  confidence: number;
  min_yield: number;
  max_yield: number;
  yield_index: number;
  recommendation_score: number;
}

export interface RecommendResponse {
  recommendations: CropRecommendation[];
}

export interface ModelMetrics {
  r2_mean: number;
  r2_std: number;
  n_samples: number;
  n_features: number;
}

export interface FeatureImportance {
  [key: string]: number;
}

export interface ModelInfo {
  model_type: string;
  n_estimators: number;
  training_samples: number;
  features: string[];
  metrics: ModelMetrics;
  feature_importance: FeatureImportance;
}

export interface ApiError {
  detail: string;
}
