import { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom'; // Import useParams
import './ProjectDetail.css'; // New CSS file for ProjectDetail

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

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>(); // Get ID from URL
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProject = async () => {
      if (!id) {
        setError('Project ID not found in URL.');
        setLoading(false);
        return;
      }
      try {
        const response = await axios.get<Project>(`${import.meta.env.VITE_API_URL}projects/${id}/`);
        setProject(response.data);
      } catch (err) {
        console.error('Failed to fetch project details:', err);
        setError('Failed to load project. Please check the project ID.');
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [id]); // Re-fetch if ID changes

  if (loading) {
    return <div className="project-detail-container"><p className="loading-message">Loading project details...</p></div>;
  }

  if (error) {
    return <div className="project-detail-container"><p className="error">{error}</p><Link to="/projects" className="btn secondary">Back to Projects</Link></div>;
  }

  if (!project) {
    return <div className="project-detail-container"><p className="no-project-found">Project not found.</p><Link to="/projects" className="btn secondary">Back to Projects</Link></div>;
  }

  return (
    <div className="project-detail-container">
      <h1 className="project-title">{project.title}</h1>

      {project.image && (
        <img src={project.image} alt={project.title} className="project-main-image" />
      )}

      <p className="project-description">{project.description}</p>

      <div className="project-meta">
        <div className="project-tags-detail">
          <strong>Tags: </strong>
          {project.tags && project.tags.map((tag, index) => (
            <span key={index} className="tag-badge">
              {tag}
            </span>
          ))}
        </div>
        <p className="project-created-at">
          <strong>Created:</strong> {new Date(project.created_at).toLocaleDateString()}
        </p>
      </div>

      <div className="project-actions">
        {project.project_url && (
          <a href={project.project_url} target="_blank" rel="noopener noreferrer" className="btn primary project-action-btn">
            View Live Project
          </a>
        )}
        {project.repo_url && (
          <a href={project.repo_url} target="_blank" rel="noopener noreferrer" className="btn secondary project-action-btn">
            View Source Code
          </a>
        )}
      </div>

      <div className="back-link">
        <Link to="/projects" className="btn secondary">
          ← Back to All Projects
        </Link>
      </div>
    </div>
  );
};

export default ProjectDetail;
