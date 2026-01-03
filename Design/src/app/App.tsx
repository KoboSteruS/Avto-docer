import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Services from './pages/Services';
import OurWorks from './pages/OurWorks';
import NewWorks from './pages/NewWorks';
import Reviews from './pages/Reviews';
import About from './pages/About';
import Contacts from './pages/Contacts';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="services" element={<Services />} />
          <Route path="our-works" element={<OurWorks />} />
          <Route path="new-works" element={<NewWorks />} />
          <Route path="reviews" element={<Reviews />} />
          <Route path="about" element={<About />} />
          <Route path="contacts" element={<Contacts />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
