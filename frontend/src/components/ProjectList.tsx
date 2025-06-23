import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom'; // Import Link for navigating to detail page
import './ProjectList.css';

interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  project_url?: string;
  repo_url?: string;
  tags: string[];
  display_order: number;
  created_at: string;
}

interface Tag {
  id: string;
  name: string;
}

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [selectedTag, setSelectedTag] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await axios.get<Tag[]>(`${import.meta.env.VITE_API_URL}tags/`);
        setAllTags(response.data);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
      }
    };
    fetchTags();
  }, []);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        let url = `${import.meta.env.VITE_API_URL}projects/`;
        if (selectedTag) {
          url = `${url}?tag=${selectedTag}`;
        }
        const response = await axios.get<Project[]>(url);
        setProjects(response.data);
      } catch (err) {
        setError('Failed to fetch projects');
        console.error(err);
      }
    };
    fetchProjects();
  }, [selectedTag]);

  return (
    <div className="project-list-container">
      <h1>All Projects</h1> {/* Changed title */}

      <div className="tag-filter-section">
        <label htmlFor="tag-select">Filter by Tag:</label>
        <select
          id="tag-select"
          value={selectedTag}
          onChange={(e) => setSelectedTag(e.target.value)}
        >
          <option value="">All Tags</option>
          {allTags.map((tag) => (
            <option key={tag.id} value={tag.name}>
              {tag.name}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="error">{error}</p>}
      <div className="projects-grid">
        {projects.length > 0 ? (
          projects.map((project) => (
            <div key={project.id} className="project-card">
              <h2>{project.title}</h2>
              <p>{project.description.substring(0, 150)}...</p> {/* Truncate for preview */}
              {project.image && (
                <img src={project.image} alt={project.title} />
              )}
              <div className="project-links">
                {project.project_url && (
                  <a
                    href={project.project_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Live
                  </a>
                )}
                {project.repo_url && (
                  <a
                    href={project.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Code
                  </a>
                )}
              </div>
              <div className="project-tags">
                {project.tags && project.tags.map((tag, index) => (
                  <span key={index} className="tag-badge">
                    {tag}
                  </span>
                ))}
              </div>
              <Link to={`/projects/${project.id}`} className="btn preview-btn"> {/* Link to detail page */}
                Learn More
              </Link>
            </div>
          ))
        ) : (
          <p>No projects found matching the criteria.</p>
        )}
      </div>
    </div>
  );
};

export default ProjectList;
