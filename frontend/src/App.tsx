import './App.css';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import HomePage from "@/pages/Home/HomePage";
import AboutPage from "@/pages/About/AboutPage";
import SearchPage from "@/pages/Search/SearchPage";
import NotFound from "@/pages/NotFound"
// import { Layout } from './components/layout/Layout';
// import { ThemeProvider } from './components/layout/ThemeProvider';


function App() {

  return (
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
  );
}

export default App
