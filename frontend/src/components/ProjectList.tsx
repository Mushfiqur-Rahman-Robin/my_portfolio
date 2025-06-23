import { useState, useEffect } from 'react';
import axios from 'axios';
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
  const [allTags, setAllTags] = useState<Tag[]>([]); // To store all available tags
  const [selectedTag, setSelectedTag] = useState<string>(''); // For filtering
  const [error, setError] = useState<string | null>(null);

  // Effect to fetch all tags
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

  // Effect to fetch projects based on selectedTag
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
      <h1>My Projects</h1>

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
              <p>{project.description}</p>
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
                    View Project
                  </a>
                )}
                {project.repo_url && (
                  <a
                    href={project.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View Repository
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
