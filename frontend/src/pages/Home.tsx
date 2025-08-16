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

const Home: React.FC = () => {
  const [featuredProjects, setFeaturedProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadingFeaturedProjects, setLoadingFeaturedProjects] = useState<boolean>(true);

  useEffect(() => {
    // Increment visitor count on page load (backend-only)
    axios.post(`${import.meta.env.VITE_API_URL}visitor-count/`)
      .catch(err => console.error('Failed to increment visitor count:', err));

    // Fetch up to 3 featured projects
    const fetchFeaturedProjects = async () => {
      setLoadingFeaturedProjects(true);
      try {
        const response = await axios.get<PaginationInfo<Project>>(
          `${import.meta.env.VITE_API_URL}projects/?is_featured=true&ordering=display_order`
        );
        // Ensure only top 3 are displayed AND that the array has at least 3
        const projects = response.data.results.slice(0, 3);
        if (projects.length === 3) { // Only set if exactly 3 projects are available
          setFeaturedProjects(projects);
          setError(null); // Clear any previous errors
        } else {
          setFeaturedProjects([]); // Clear projects if not exactly 3
          setError("Not enough featured projects to display. Need exactly 3."); // Provide specific error message
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
          </div>
        </div>
      </section>

      <SkillsSection />

      {/* Conditional rendering for Featured Projects section */}
      {!loadingFeaturedProjects && featuredProjects.length === 3 && (
        <section className="featured-projects-section">
          <h2>Featured Projects</h2>
          {error && <p className="error">{error}</p>}
          <div className="projects-preview-grid">
            {featuredProjects.map((project) => (
                <div key={project.id} className="project-preview-card">
                  <Link to={`/projects/${project.id}`} className="project-card-banner-link">
                    <h3>{project.title}</h3>
                    {project.image && (
                      <img src={project.image} alt={project.title} className="project-preview-image" />
                    )}
                    <p className="project-preview-description">
                      {/* Apply stripHtmlTags here before substring */}
                      {stripHtmlTags(project.description).substring(0, 100)}...
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
      {!loadingFeaturedProjects && featuredProjects.length !== 3 && (
        <section className="featured-projects-section">
          <h2>Featured Projects</h2>
          {error && <p className="error">{error}</p>}
          <p className="no-featured-projects">No featured projects to display. Mark exactly 3 projects as featured in Django admin to show this section!</p>
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
