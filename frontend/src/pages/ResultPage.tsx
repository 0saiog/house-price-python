/**
 * The prediction, and the inputs it came from.
 *
 * Reached only through a navigation carrying state; opening `/result` directly
 * sends the visitor back to the form rather than showing an empty page.
 */

import { Link, Navigate, useLocation } from "react-router-dom";
import type { PredictionRequest, PredictionResponse } from "../types/prediction";

interface ResultState {
  result: PredictionResponse;
  request: PredictionRequest;
}

export function ResultPage() {
  const location = useLocation();
  const state = location.state as ResultState | null;

  if (!state?.result) return <Navigate to="/" replace />;
  const { result, request } = state;

  return (
    <>
      <header className="hero">
        <h1>Estimated price</h1>
      </header>

      <div className="card result">
        <p className="price">₹ {result.predicted_price_formatted}</p>
        <p className="price-exact">
          {result.predicted_price.toLocaleString("en-IN", { maximumFractionDigits: 0 })} {result.currency}
        </p>

        {!result.location_known && (
          <p className="alert" role="status">
            The model has no column for <strong>{request.location}</strong>, so this estimate comes
            from the catch-all bucket and is weaker than it would be for a listed city.
          </p>
        )}

        <dl className="summary">
          <div><dt>City</dt><dd>{request.location.replace(/-/g, " ")}</dd></div>
          <div><dt>Area</dt><dd>{request.area_sqft.toLocaleString("en-IN")} sqft {request.is_carpet_area ? "(carpet)" : "(super)"}</dd></div>
          <div><dt>Furnishing</dt><dd>{request.furnishing}</dd></div>
          <div><dt>Transaction</dt><dd>{request.transaction}</dd></div>
          {request.bathroom !== undefined && <div><dt>Bathrooms</dt><dd>{request.bathroom}</dd></div>}
          {request.balcony !== undefined && <div><dt>Balconies</dt><dd>{request.balcony}</dd></div>}
          {request.floor_num !== undefined && (
            <div><dt>Floor</dt><dd>{request.floor_num}{request.total_floors !== undefined ? ` of ${request.total_floors}` : ""}</dd></div>
          )}
        </dl>

        <p className="caveat">
          Typical error is around 17.5% (median absolute percentage error on a held-out test set of
          listings the model never saw). Treat it as a starting point, not a valuation.
        </p>

        <Link className="button" to="/">Price another property</Link>
      </div>
    </>
  );
}
