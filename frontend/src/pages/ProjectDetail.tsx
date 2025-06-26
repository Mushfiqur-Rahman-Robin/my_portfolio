import { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './css/ProjectDetail.css';

interface ProjectImage {
  id: string;
  image: string; // URL of the gallery image
  caption: string;
  display_order: number;
}

interface Project {
  id: string;
  title: string;
  description: string;
  image: string; // Main banner image
  project_url?: string;
  repo_url?: string;
  tags: string[];
  code_snippet?: string; // New field
  gallery_images: ProjectImage[]; // New field for gallery
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
          setSelectedGalleryImage(response.data.gallery_images[0].image); // Set first gallery image as default
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

  if (loading) {
    return <div className="project-detail-container"><p className="loading-message">Loading project details...</p></div>;
  }

  if (error) {
    return <div className="project-detail-container"><p className="error">{error}</p><Link to="/projects" className="btn secondary">Back to Projects</Link></div>;
  }

  if (!project) {
    return <div className="project-detail-container"><p className="no-project-found">Project not found.</p><Link to="/projects" className="btn secondary">Back to Projects</Link></div>;
  }

  // Determine the language for syntax highlighting (can be made dynamic based on tags or a new field)
  const codeLanguage = project.tags.includes('Python') ? 'python' :
                       project.tags.includes('JavaScript') || project.tags.includes('TypeScript') || project.tags.includes('React') ? 'javascript' :
                       'plaintext'; // Default to plaintext if language not found

  return (
    <div className="project-detail-container">
      <h1 className="project-title">{project.title}</h1>

      {/* Main project banner image (from 'image' field) */}
      {project.image && (
        <img src={project.image} alt={project.title} className="project-main-image" />
      )}

      {/* Project Gallery */}
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

      <p className="project-description">{project.description}</p>

      {project.code_snippet && (
        <div className="code-snippet-section">
          <h2>Code Snippet</h2>
          <SyntaxHighlighter language={codeLanguage} style={dark} showLineNumbers>
            {project.code_snippet}
          </SyntaxHighlighter>
        </div>
      )}

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
