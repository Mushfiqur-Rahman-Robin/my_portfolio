import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import SkillsSection from '../components/SkillsSection.tsx';
import './css/Home.css';
import { stripHtmlTags } from '../utils/html_cleaner'; // Import the utility


interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  project_url?: string;
  repo_url?: string;
  tags: string[];
}

interface PaginationInfo<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.substring(0, maxLength).trim()}....`;
};

const Home: React.FC = () => {
  const [featuredProjects, setFeaturedProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadingFeaturedProjects, setLoadingFeaturedProjects] = useState<boolean>(true);
  const [calendlyUrl, setCalendlyUrl] = useState<string>("");

  useEffect(() => {
    // Increment visitor count on page load (backend-only)
    axios.post(`${import.meta.env.VITE_API_URL}visitor-count/`)
      .catch(err => console.error('Failed to increment visitor count:', err));

    // Fetch booking configuration for Calendly
    axios.get(`${import.meta.env.VITE_API_URL}booking-config/`)
      .then(response => {
        if (response.data.calendly_url) {
          setCalendlyUrl(response.data.calendly_url);
        }
      })
      .catch(err => console.error('Failed to fetch site config:', err));

    // Fetch up to 3 featured projects
    const fetchFeaturedProjects = async () => {
      setLoadingFeaturedProjects(true);
      try {
        const response = await axios.get<PaginationInfo<Project>>(
          `${import.meta.env.VITE_API_URL}projects/?is_featured=true&ordering=display_order`
        );
        // Show up to top 3 featured projects
        const projects = response.data.results.slice(0, 3);
        if (projects.length > 0) {
          setFeaturedProjects(projects);
          setError(null);
        } else {
          setFeaturedProjects([]);
          setError('No featured projects found yet. Please mark at least one project as featured in Django admin.');
        }
      } catch (err) {
        setFeaturedProjects([]); // Clear projects on error
        setError("Failed to fetch featured projects.");
        console.error("Featured projects fetch error:", err);
      } finally {
        setLoadingFeaturedProjects(false);
      }
    };
    fetchFeaturedProjects();
  }, []);

  return (
    <div className="home-container">
      <section className="hero-banner">
        <div className="banner-content">
          <h1>Hello, I'm Md Mushfiqur Rahman</h1>
          <p className="tagline">AI/ML Engineer | Strategist | Problem Solver</p>
          <p className="intro-text">
            Empowering systems with intelligence. I lead the design and implementation of sophisticated ML, Generative AI, and agentic solutions, bridging ideas to impactful outcomes.
          </p>
          <div className="banner-cta-buttons">
            <Link to="/projects" className="btn primary">
              View My Work
            </Link>
            <Link to="/contact" className="btn secondary">
              Let's Connect
            </Link>
            <span
              className="btn buy-me-coffee-btn disabled-bmac"
              title="Buy Me A Coffee is currently unavailable"
              aria-disabled="true"
            >
              Buy Me A Coffee
            </span>
            {calendlyUrl && (
              <a
                href={calendlyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn calendly-btn"
                title="Book a session with me on Calendly"
              >
                Book a Session
              </a>
            )}
          </div>
        </div>
      </section>

      <SkillsSection />

      {/* Conditional rendering for Featured Projects section */}
      {!loadingFeaturedProjects && featuredProjects.length > 0 && (
        <section className="featured-projects-section">
          <h2>Featured Projects</h2>
          {error && <p className="error">{error}</p>}
          <div className="projects-preview-grid">
            {featuredProjects.map((project) => (
                <div key={project.id} className="project-preview-card">
                  <Link to={`/projects/${project.id}`} className="project-card-banner-link">
                    <h3>{truncateText(project.title, 74)}</h3>
                    {project.image && (
                      <div className="project-preview-image-frame">
                        <img src={project.image} alt={project.title} className="project-preview-image" />
                      </div>
                    )}
                    <p className="project-preview-description">
                      {truncateText(stripHtmlTags(project.description), 165)}
                    </p>
                    <div className="project-preview-tags">
                      {project.tags && project.tags.map((tag, index) => (
                        <span key={index} className="tag-badge">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </Link>
                  <div className="project-preview-actions">
                    {project.project_url && (
                      <a href={project.project_url} target="_blank" rel="noopener noreferrer" className="btn primary">
                        View Live
                      </a>
                    )}
                    {project.repo_url && (
                      <a href={project.repo_url} target="_blank" rel="noopener noreferrer" className="btn secondary">
                        View Code
                      </a>
                    )}
                  </div>
                </div>
              ))}
          </div>
          <div className="all-projects-link">
            <Link to="/projects" className="btn secondary">
              View All Projects
            </Link>
          </div>
        </section>
      )}
      {!loadingFeaturedProjects && featuredProjects.length === 0 && (
        <section className="featured-projects-section">
          <h2>Featured Projects</h2>
          {error && <p className="error">{error}</p>}
          <p className="no-featured-projects">No featured projects to display right now. Please mark projects as featured in Django admin to show this section.</p>
          <div className="all-projects-link">
            <Link to="/projects" className="btn secondary">
              View All Projects
            </Link>
          </div>
        </section>
      )}
      {loadingFeaturedProjects && (
        <section className="featured-projects-section">
          <h2>Featured Projects</h2>
          <p className="loading-message">Loading featured projects...</p>
        </section>
      )}
    </div>
  );
};

export default Home;
