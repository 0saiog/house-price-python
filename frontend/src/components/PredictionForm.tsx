/**
 * The property form.
 *
 * Validation runs here before anything is sent: the API validates too, but a
 * round trip is a slow way to tell someone they left the area blank.
 */

import { useEffect, useState } from "react";
import { fetchLocations } from "../api/predictionClient";
import type { PredictionRequest } from "../types/prediction";

const FURNISHING = ["Furnished", "Semi-Furnished", "Unfurnished"];
const TRANSACTION = ["Resale", "New Property"];
const OWNERSHIP = ["Freehold", "Leasehold", "Co-operative Society", "Power Of Attorney"];
const FACING = ["East", "West", "North", "South", "North - East", "North - West", "South - East", "South - West"];

/** The form's own state: every field is a string, as HTML inputs give them. */
interface FormState {
  location: string;
  area_sqft: string;
  is_carpet_area: string;
  furnishing: string;
  transaction: string;
  bathroom: string;
  balcony: string;
  car_parking: string;
  parking_covered: boolean;
  floor_num: string;
  total_floors: string;
  ownership: string;
  facing: string;
  overlooking_garden: boolean;
  overlooking_pool: boolean;
  overlooking_main_road: boolean;
}

const INITIAL: FormState = {
  location: "",
  area_sqft: "",
  is_carpet_area: "true",
  furnishing: "Semi-Furnished",
  transaction: "Resale",
  bathroom: "2",
  balcony: "1",
  car_parking: "1",
  parking_covered: true,
  floor_num: "3",
  total_floors: "10",
  ownership: "Freehold",
  facing: "",
  overlooking_garden: false,
  overlooking_pool: false,
  overlooking_main_road: false,
};

type Errors = Partial<Record<keyof FormState, string>>;

/** Field-level validation. An empty object means the form is submittable. */
function validate(form: FormState): Errors {
  const errors: Errors = {};
  if (!form.location) errors.location = "Choose a city.";

  const area = Number(form.area_sqft);
  if (!form.area_sqft.trim()) errors.area_sqft = "Enter the floor area.";
  else if (!Number.isFinite(area) || area <= 0) errors.area_sqft = "Area must be a number greater than 0.";
  else if (area > 1_000_000) errors.area_sqft = "That is over a million square feet - check the number.";

  const nonNegative: [keyof FormState, string][] = [
    ["bathroom", "Bathrooms"],
    ["balcony", "Balconies"],
    ["car_parking", "Parking spaces"],
    ["total_floors", "Building height"],
  ];
  for (const [field, label] of nonNegative) {
    const raw = form[field] as string;
    if (raw.trim() && (!Number.isFinite(Number(raw)) || Number(raw) < 0)) {
      errors[field] = `${label} cannot be negative.`;
    }
  }

  const floors = Number(form.total_floors);
  const floor = Number(form.floor_num);
  if (form.floor_num.trim() && form.total_floors.trim() && Number.isFinite(floor) && Number.isFinite(floors) && floor > floors) {
    errors.floor_num = "The flat cannot be above the top floor.";
  }
  return errors;
}

/** An optional number field: blank means "not provided", not zero. */
function optionalNumber(raw: string): number | undefined {
  const trimmed = raw.trim();
  if (!trimmed) return undefined;
  const value = Number(trimmed);
  return Number.isFinite(value) ? value : undefined;
}

/** Builds the API payload from validated form state. */
function toRequest(form: FormState): PredictionRequest {
  return {
    location: form.location,
    area_sqft: Number(form.area_sqft),
    furnishing: form.furnishing,
    transaction: form.transaction,
    is_carpet_area: form.is_carpet_area === "true",
    bathroom: optionalNumber(form.bathroom),
    balcony: optionalNumber(form.balcony),
    car_parking: optionalNumber(form.car_parking),
    parking_covered: form.parking_covered,
    floor_num: optionalNumber(form.floor_num),
    total_floors: optionalNumber(form.total_floors),
    ownership: form.ownership || undefined,
    facing: form.facing || undefined,
    overlooking_garden: form.overlooking_garden,
    overlooking_pool: form.overlooking_pool,
    overlooking_main_road: form.overlooking_main_road,
  };
}

interface Props {
  /** Called with the payload once the form validates. */
  onSubmit: (request: PredictionRequest) => void;
  /** Disables the form while a request is in flight. */
  loading: boolean;
}

export function PredictionForm({ onSubmit, loading }: Props) {
  const [form, setForm] = useState<FormState>(INITIAL);
  const [errors, setErrors] = useState<Errors>({});
  const [submitted, setSubmitted] = useState(false);
  const [locations, setLocations] = useState<string[]>([]);
  const [locationsError, setLocationsError] = useState<string | null>(null);

  // The dropdown is populated from the API, so it can only ever offer cities the
  // loaded model actually has a column for.
  useEffect(() => {
    fetchLocations()
      .then(setLocations)
      .catch((e: Error) => setLocationsError(e.message));
  }, []);

  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    const next = { ...form, [key]: value };
    setForm(next);
    if (submitted) setErrors(validate(next));
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitted(true);
    const found = validate(form);
    setErrors(found);
    if (Object.keys(found).length === 0) onSubmit(toRequest(form));
  };

  const field = (key: keyof FormState) =>
    errors[key] ? <span className="field-error">{errors[key]}</span> : null;

  return (
    <form className="card" onSubmit={handleSubmit} noValidate>
      <div className="grid">
        <label>
          <span className="label-text">
            City <span className="required" aria-hidden="true">*</span>
          </span>
          <select
            value={form.location}
            onChange={(e) => set("location", e.target.value)}
            aria-invalid={Boolean(errors.location)}
          >
            <option value="">Select a city</option>
            {locations.map((city) => (
              <option key={city} value={city}>
                {city.replace(/-/g, " ")}
              </option>
            ))}
          </select>
          {locationsError && <span className="field-error">{locationsError}</span>}
          {field("location")}
        </label>

        <label>
          <span className="label-text">
            Area (sqft) <span className="required" aria-hidden="true">*</span>
          </span>
          <input
            type="number"
            min="1"
            step="any"
            inputMode="decimal"
            placeholder="1200"
            value={form.area_sqft}
            onChange={(e) => set("area_sqft", e.target.value)}
            aria-invalid={Boolean(errors.area_sqft)}
          />
          {field("area_sqft")}
        </label>

        <label>
          Area type
          <select value={form.is_carpet_area} onChange={(e) => set("is_carpet_area", e.target.value)}>
            <option value="true">Carpet area</option>
            <option value="false">Super area</option>
          </select>
        </label>

        <label>
          Furnishing
          <select value={form.furnishing} onChange={(e) => set("furnishing", e.target.value)}>
            {FURNISHING.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </label>

        <label>
          Transaction
          <select value={form.transaction} onChange={(e) => set("transaction", e.target.value)}>
            {TRANSACTION.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </label>

        <label>
          Ownership
          <select value={form.ownership} onChange={(e) => set("ownership", e.target.value)}>
            <option value="">Not specified</option>
            {OWNERSHIP.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </label>

        <label>
          Bathrooms
          <input type="number" min="0" step="1" value={form.bathroom} onChange={(e) => set("bathroom", e.target.value)} />
          {field("bathroom")}
        </label>

        <label>
          Balconies
          <input type="number" min="0" step="1" value={form.balcony} onChange={(e) => set("balcony", e.target.value)} />
          {field("balcony")}
        </label>

        <label>
          Parking spaces
          <input type="number" min="0" step="1" value={form.car_parking} onChange={(e) => set("car_parking", e.target.value)} />
          {field("car_parking")}
        </label>

        <label>
          Floor
          <input type="number" step="1" value={form.floor_num} onChange={(e) => set("floor_num", e.target.value)} />
          {field("floor_num")}
        </label>

        <label>
          Floors in building
          <input type="number" min="0" step="1" value={form.total_floors} onChange={(e) => set("total_floors", e.target.value)} />
          {field("total_floors")}
        </label>

        <label>
          Facing
          <select value={form.facing} onChange={(e) => set("facing", e.target.value)}>
            <option value="">Not specified</option>
            {FACING.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </label>
      </div>

      <fieldset className="checks">
        <legend>Extras</legend>
        <label className="check">
          <input type="checkbox" checked={form.parking_covered} onChange={(e) => set("parking_covered", e.target.checked)} />
          Covered parking
        </label>
        <label className="check">
          <input type="checkbox" checked={form.overlooking_garden} onChange={(e) => set("overlooking_garden", e.target.checked)} />
          Overlooks a garden
        </label>
        <label className="check">
          <input type="checkbox" checked={form.overlooking_pool} onChange={(e) => set("overlooking_pool", e.target.checked)} />
          Overlooks a pool
        </label>
        <label className="check">
          <input type="checkbox" checked={form.overlooking_main_road} onChange={(e) => set("overlooking_main_road", e.target.checked)} />
          Overlooks a main road
        </label>
      </fieldset>

      <button type="submit" disabled={loading}>
        {loading ? "Predicting..." : "Predict price"}
      </button>
    </form>
  );
}
