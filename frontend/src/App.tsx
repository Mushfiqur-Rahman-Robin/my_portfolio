import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.tsx';
import Footer from './components/Footer.tsx';
import Home from './pages/Home.tsx';
import About from './pages/About.tsx';
import Contact from './pages/Contact.tsx';
import ProjectList from './components/ProjectList.tsx';
import ProjectDetail from './pages/ProjectDetail.tsx';
import Resume from './pages/Resume.tsx';
import ExperienceList from './pages/ExperienceList.tsx';
import ExperienceDetail from './pages/ExperienceDetail.tsx';
import CertificationList from './pages/CertificationList.tsx';
import AchievementList from './pages/AchievementList.tsx';
import PublicationList from './pages/PublicationList.tsx';
import ChatbotWidget from './components/ChatbotWidget.tsx';

import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/projects/:id" element={<ProjectDetail />} />
            <Route path="/resume" element={<Resume />} />
            <Route path="/experience" element={<ExperienceList />} />
            <Route path="/experience/:id" element={<ExperienceDetail />} />
            <Route path="/certifications" element={<CertificationList />} />
            <Route path="/achievements" element={<AchievementList />} />
            <Route path="/publications" element={<PublicationList />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </main>
        <Footer />
      </div>
      <ChatbotWidget />
    </Router>
  );
}

export default App;
