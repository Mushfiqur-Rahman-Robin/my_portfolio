import { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import './css/ProjectDetail.css';

interface ProjectImage {
  id: string;
  image: string;
  caption: string;
  display_order: number;
}

interface Project {
  id: string;
  title: string;
  description: string; // This contains the rich HTML content
  image: string;
  project_url?: string;
  repo_url?: string;
  tags: string[];
  gallery_images: ProjectImage[];
  display_order: number;
  created_at: string;
}

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedGalleryImage, setSelectedGalleryImage] = useState<string | undefined>(undefined);

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
        if (response.data.gallery_images && response.data.gallery_images.length > 0) {
          setSelectedGalleryImage(response.data.gallery_images[0].image);
        }
      } catch (err) {
        console.error('Failed to fetch project details:', err);
        setError('Failed to load project. Please check the project ID.');
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [id]);

  // Highlight code blocks after content is loaded
  useEffect(() => {
    if (!loading && project) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        if (window.hljs) {
          window.hljs.highlightAll();
        }
      }, 100);
    }
  }, [loading, project]);

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

      {project.gallery_images && project.gallery_images.length > 0 && (
        <div className="project-gallery">
          <div className="selected-gallery-image-container">
            <img src={selectedGalleryImage || project.gallery_images[0].image} alt="Project Gallery" className="selected-gallery-image" />
          </div>
          <div className="gallery-thumbnails">
            {project.gallery_images.map((img) => (
              <img
                key={img.id}
                src={img.image}
                alt={img.caption}
                className={`thumbnail-image ${selectedGalleryImage === img.image ? 'active' : ''}`}
                onClick={() => setSelectedGalleryImage(img.image)}
              />
            ))}
          </div>
        </div>
      )}

      <div
        className="project-rich-content"
        dangerouslySetInnerHTML={{ __html: project.description }}
      />

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
