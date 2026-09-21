import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import SearchPage from "./pages/SearchPage";
import DocumentsPage from "./pages/DocumentsPage";
import EvaluationPage from "./pages/EvaluationPage";
import AboutPage from "./pages/AboutPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<SearchPage />} />
        <Route path="dokumenti" element={<DocumentsPage />} />
        <Route path="evaluacija" element={<EvaluationPage />} />
        <Route path="o-radu" element={<AboutPage />} />
      </Route>
    </Routes>
  );
}
