import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.tsx';
import Footer from './components/Footer.tsx';
import Home from './pages/Home.tsx';

const About = lazy(() => import('./pages/About.tsx'));
const Contact = lazy(() => import('./pages/Contact.tsx'));
const ProjectList = lazy(() => import('./components/ProjectList.tsx'));
const ProjectDetail = lazy(() => import('./pages/ProjectDetail.tsx'));
const Resume = lazy(() => import('./pages/Resume.tsx'));
const ExperienceList = lazy(() => import('./pages/ExperienceList.tsx'));
const ExperienceDetail = lazy(() => import('./pages/ExperienceDetail.tsx'));
const CertificationList = lazy(() => import('./pages/CertificationList.tsx'));
const AchievementList = lazy(() => import('./pages/AchievementList.tsx'));
const PublicationList = lazy(() => import('./pages/PublicationList.tsx'));
const ChatbotWidget = lazy(() => import('./components/ChatbotWidget.tsx'));

import './App.css';

const PageLoader = () => (
  <div className="loading-message" style={{ padding: '4rem 1rem', textAlign: 'center' }}>
    Loading...
  </div>
);

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <main className="content">
          <Suspense fallback={<PageLoader />}>
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
          </Suspense>
        </main>
        <Footer />
      </div>
      <Suspense fallback={null}>
        <ChatbotWidget />
      </Suspense>
    </Router>
  );
}

export default App;
