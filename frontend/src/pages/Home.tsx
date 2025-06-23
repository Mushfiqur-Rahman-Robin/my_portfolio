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
        // Fetch projects ordered by display_order, limited to 3
        const response = await axios.get<Project[]>(`${import.meta.env.VITE_API_URL}projects/?ordering=display_order`);
        setFeaturedProjects(response.data.slice(0, 3)); // Ensure only top 3
      } catch (err) {
        setError("Failed to fetch featured projects");
        console.error(err);
      }
    };
    fetchFeaturedProjects();
  }, []);

  return (
    <div className="home-container">
      <section className="hero-banner">
        <div className="banner-content">
          <h1>Hello, I'm [Your Name]</h1> {/* Replace with your name */}
          <p className="tagline">Full-Stack Developer | Innovator | Problem Solver</p>
          <p className="intro-text">
            Crafting robust and scalable web solutions with Django, React, and modern DevOps practices.
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

      <SkillsSection /> {/* Integrated Skills Section */}

      <section className="featured-projects-section">
        <h2>Featured Projects</h2>
        {error && <p className="error">{error}</p>}
        <div className="projects-preview-grid">
          {featuredProjects.length > 0 ? (
            featuredProjects.map((project) => (
              <div key={project.id} className="project-preview-card">
                <h3>{project.title}</h3>
                {project.image && (
                  <img src={project.image} alt={project.title} />
                )}
                <p className="project-preview-description">{project.description.substring(0, 100)}...</p> {/* Truncate description */}
                <div className="project-preview-tags">
                  {project.tags && project.tags.map((tag, index) => (
                    <span key={index} className="tag-badge">
                      {tag}
                    </span>
                  ))}
                </div>
                <Link to={`/projects/${project.id}`} className="btn preview-btn"> {/* Link to detail page */}
                  View Details
                </Link>
              </div>
            ))
          ) : (
            <p>No featured projects to display.</p>
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
