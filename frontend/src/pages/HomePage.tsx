/**
 * The form page. Owns the request lifecycle: loading, error, and handing the
 * result to the result page through router state.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { predictPrice } from "../api/predictionClient";
import { PredictionForm } from "../components/PredictionForm";
import type { PredictionRequest, PredictionResponse } from "../types/prediction";

export function HomePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (request: PredictionRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result: PredictionResponse = await predictPrice(request);
      navigate("/result", { state: { result, request } });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <header className="hero">
        <h1>What is this flat worth?</h1>
        <p>
          A price estimate from a gradient boosting model trained on 187,000 Indian property
          listings with pandas and scikit-learn, served by FastAPI.
        </p>
      </header>

      {error && (
        <div className="alert" role="alert">
          <strong>Could not get a prediction.</strong> {error}
        </div>
      )}

      <PredictionForm onSubmit={handleSubmit} loading={loading} />
    </>
  );
}
