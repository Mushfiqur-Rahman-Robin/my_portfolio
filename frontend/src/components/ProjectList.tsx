import { useState, useEffect } from 'react'; // Keep only specific hooks
import axios from 'axios';
import './ProjectList.css'; // Create this new CSS file

interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  project_url?: string;
  repo_url?: string;
  tags: string;
  display_order: number;
  created_at: string;
}

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}projects/`,
        );
        setProjects(response.data);
      } catch (err) {
        setError('Failed to fetch projects');
        console.error(err);
      }
    };
    fetchProjects();
  }, []);

  return (
    <div className="project-list-container">
      <h1>My Projects</h1>
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
              <p className="project-tags">Tags: {project.tags}</p>
            </div>
          ))
        ) : (
          <p>No projects found.</p>
        )}
      </div>
    </div>
  );
};

export default ProjectList;
