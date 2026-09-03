/**
 * Mirrors the backend schemas in `backend/src/schemas/prediction.rs`.
 * Optional fields are optional there too: the model imputes what it is not told
 * rather than forcing the form to invent a zero.
 */

export interface PredictionRequest {
  location: string;
  area_sqft: number;
  furnishing: string;
  transaction: string;
  is_carpet_area?: boolean;
  bathroom?: number;
  balcony?: number;
  car_parking?: number;
  parking_covered?: boolean;
  floor_num?: number;
  total_floors?: number;
  ownership?: string;
  facing?: string;
  overlooking_garden?: boolean;
  overlooking_pool?: boolean;
  overlooking_main_road?: boolean;
}

export interface PredictionResponse {
  predicted_price: number;
  predicted_price_formatted: string;
  currency: string;
  /** False when the city fell into the model's `other` bucket. */
  location_known: boolean;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  features: number;
  layers: number[];
}
