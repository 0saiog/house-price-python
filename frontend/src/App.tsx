/** Routes: the form, the result, and a 404 for everything else. */

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { ResultPage } from "./pages/ResultPage";

export default function App() {
  return (
    <BrowserRouter>
      <main className="shell">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/result" element={<ResultPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
        <footer className="foot">
          House price prediction - Rust end to end: Vearo for the model, FastAPI for the API.
        </footer>
      </main>
    </BrowserRouter>
  );
}
