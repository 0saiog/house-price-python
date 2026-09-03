/** 404. */

import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="card">
      <h1>404</h1>
      <p>That page does not exist.</p>
      <Link className="button" to="/">Back to the form</Link>
    </div>
  );
}
