import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import SkillsSection from '../components/SkillsSection.tsx';
import './Home.css';

interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  project_url?: string;
  repo_url?: string;
  tags: string[];
}

const Home: React.FC = () => {
  const [featuredProjects, setFeaturedProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Increment visitor count on page load (backend-only)
    axios.post(`${import.meta.env.VITE_API_URL}visitor-count/`)
      .catch(err => console.error('Failed to increment visitor count:', err));

    // Fetch up to 3 featured projects
    const fetchFeaturedProjects = async () => {
      try {
        // CRITICAL FIX: Explicitly filter for is_featured=true
        const response = await axios.get<Project[]>(
          `${import.meta.env.VITE_API_URL}projects/?is_featured=true&ordering=display_order`
        );
        setFeaturedProjects(response.data.slice(0, 3)); // Ensure only top 3 are displayed
      } catch (err) {
        setError("Failed to fetch featured projects");
        console.error("Featured projects fetch error:", err);
      }
    };
    fetchFeaturedProjects();
  }, []);

  return (
    <div className="home-container">
      <section className="hero-banner">
        <div className="banner-content">
          <h1>Hello, I'm Md Mushfiqur Rahman</h1> {/* Updated name */}
          <p className="tagline">AI/ML Engineer | Innovator | Problem Solver</p> {/* Updated tagline */}
          <p className="intro-text">
            Crafting robust and scalable AI-powered solutions and web applications with Django, React, and modern DevOps practices.
          </p>
          <div className="banner-cta-buttons">
            <Link to="/projects" className="btn primary">
              View My Work
            </Link>
            <Link to="/contact" className="btn secondary">
              Let's Connect
            </Link>
            <a
              href="https://www.buymeacoffee.com/yourusername" // Replace with your Buy Me a Coffee link
              target="_blank"
              rel="noopener noreferrer"
              className="btn buy-me-coffee-btn"
            >
              Buy Me A Coffee
            </a>
          </div>
        </div>
      </section>

      <SkillsSection />

      <section className="featured-projects-section">
        <h2>Featured Projects</h2>
        {error && <p className="error">{error}</p>}
        <div className="projects-preview-grid">
          {featuredProjects.length > 0 ? (
            featuredProjects.map((project) => (
              <div key={project.id} className="project-preview-card">
                <Link to={`/projects/${project.id}`} className="project-card-banner-link"> {/* Link whole image area to detail */}
                  <h3>{project.title}</h3>
                  {project.image && (
                    <img src={project.image} alt={project.title} className="project-preview-image" />
                  )}
                  <p className="project-preview-description">{project.description.substring(0, 100)}...</p>
                  <div className="project-preview-tags">
                    {project.tags && project.tags.map((tag, index) => (
                      <span key={index} className="tag-badge">
                        {tag}
                      </span>
                    ))}
                  </div>
                </Link>
                <div className="project-preview-actions"> {/* Separate actions from linked area */}
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
            ))
          ) : (
            <p className="no-featured-projects">No featured projects to display. Mark projects as featured in Django admin!</p>
          )}
        </div>
        <div className="all-projects-link">
          <Link to="/projects" className="btn secondary">
            View All Projects
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
