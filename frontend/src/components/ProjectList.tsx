import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom'; // Import useSearchParams for pagination
import './css/ProjectList.css';

interface Project {
  id: string;
  title: string;
  description: string;
  image: string; // This is now the banner image
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

interface PaginationInfo {
  count: number;
  next: string | null;
  previous: string | null;
  results: Project[];
}

// Define the page size for the frontend calculation
const PROJECTS_PER_PAGE = 3; // <--- ADD THIS CONSTANT AND USE IT BELOW

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [selectedTag, setSelectedTag] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [currentPage, setCurrentPage] = useState<number>(
    parseInt(searchParams.get('page') || '1'),
  );
  const [totalPages, setTotalPages] = useState<number>(1);

  // Effect to fetch all tags
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await axios.get<Tag[]>(
          `${import.meta.env.VITE_API_URL}tags/`,
        );
        setAllTags(response.data);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
      }
    };
    fetchTags();
  }, []);

  // Effect to fetch projects based on selectedTag and current page
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        let url = `${import.meta.env.VITE_API_URL}projects/`;
        const params = new URLSearchParams();
        if (selectedTag) {
          params.append('tag', selectedTag);
        }
        params.append('page', currentPage.toString());
        // Add page_size to the request if you want to explicitly control it from frontend,
        // otherwise rely on backend default which we just changed.
        // For consistency, it's good to explicitly ask for the same page size.
        params.append('page_size', PROJECTS_PER_PAGE.toString()); // <--- ADD THIS LINE

        url = `${url}?${params.toString()}`;

        const response = await axios.get<PaginationInfo>(url);
        setProjects(response.data.results);
        // CRITICAL FIX: Base totalPages on the new PROJECTS_PER_PAGE
        setTotalPages(Math.ceil(response.data.count / PROJECTS_PER_PAGE));
      } catch (err) {
        setError('Failed to fetch projects');
        console.error(err);
      }
    };
    fetchProjects();
    setSearchParams({ page: currentPage.toString(), tag: selectedTag });
  }, [selectedTag, currentPage, setSearchParams]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="project-list-container">
      <h1>All Projects</h1>

      <div className="tag-filter-section">
        <label htmlFor="tag-select">Filter by Tag:</label>
        <select
          id="tag-select"
          value={selectedTag}
          onChange={(e) => {
            setSelectedTag(e.target.value);
            setCurrentPage(1); // Reset to first page on tag change
          }}
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
              <Link to={`/projects/${project.id}`} className="project-card-link"> {/* Link whole card preview */}
                <h2>{project.title}</h2>
                {project.image && (
                  <img src={project.image} alt={project.title} />
                )}
                <p>{project.description.substring(0, 150)}...</p>{' '}
                {/* Truncate for preview */}
                <div className="project-tags">
                  {project.tags &&
                    project.tags.map((tag, index) => (
                      <span key={index} className="tag-badge">
                        {tag}
                      </span>
                    ))}
                </div>
              </Link>
              <div className="project-card-actions"> {/* Separate container for action buttons */}
                {project.project_url && (
                  <a
                    href={project.project_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn primary"
                  >
                    View Live
                  </a>
                )}
                {project.repo_url && (
                  <a
                    href={project.repo_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn secondary"
                  >
                    View Code
                  </a>
                )}
                <Link to={`/projects/${project.id}`} className="btn secondary">
                  Learn More
                </Link>
              </div>
            </div>
          ))
        ) : (
          <p>No projects found matching the criteria.</p>
        )}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="btn pagination-btn"
          >
            Previous
          </button>
          {[...Array(totalPages)].map((_, index) => (
            <button
              key={index}
              onClick={() => handlePageChange(index + 1)}
              className={`btn pagination-btn ${
                currentPage === index + 1 ? 'active' : ''
              }`}
            >
              {index + 1}
            </button>
          ))}
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="btn pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ProjectList;
