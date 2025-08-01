// frontend/src/components/ProjectList.tsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom';
import './css/ProjectList.css';
import { stripHtmlTags } from '../utils/html_cleaner'; // Import the utility


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
const PROJECTS_PER_PAGE = 3;

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // Add loading state

  const [searchParams, setSearchParams] = useSearchParams();

  // State initialized from URL params, or default to '1' and ''
  const [currentPage, setCurrentPage] = useState<number>(() =>
    parseInt(searchParams.get('page') || '1'),
  );
  const [selectedTag, setSelectedTag] = useState<string>(() =>
    searchParams.get('tag') || '',
  );
  const [totalPages, setTotalPages] = useState<number>(1);

  // Effect to synchronize internal state from URL search params (for back/forward navigation)
  // This ensures that if the browser's back/forward button changes the URL,
  // our component's internal state updates to match.
  useEffect(() => {
    const pageFromUrl = parseInt(searchParams.get('page') || '1');
    const tagFromUrl = searchParams.get('tag') || '';

    // Only update state if it's different from what's in the URL
    if (currentPage !== pageFromUrl) {
      setCurrentPage(pageFromUrl);
    }
    if (selectedTag !== tagFromUrl) {
      setSelectedTag(tagFromUrl);
    }
  }, [searchParams]); // Depend only on searchParams itself, React Router ensures it changes when the URL does.

  // Effect to fetch all tags (runs once on mount)
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

  // Effect to fetch projects based on selectedTag and currentPage state
  useEffect(() => {
    const fetchProjects = async () => {
      setLoading(true); // Set loading true at the start of fetch
      try {
        let url = `${import.meta.env.VITE_API_URL}projects/`;
        const params = new URLSearchParams();
        if (selectedTag) {
          params.append('tag', selectedTag);
        }
        params.append('page', currentPage.toString());
        params.append('page_size', PROJECTS_PER_PAGE.toString());

        url = `${url}?${params.toString()}`;

        const response = await axios.get<PaginationInfo>(url);
        setProjects(response.data.results);
        setTotalPages(Math.ceil(response.data.count / PROJECTS_PER_PAGE));
        setError(null); // Clear any previous errors on successful fetch
      } catch (err) {
        setError('Failed to fetch projects');
        console.error(err);
        setProjects([]); // Clear projects on error to show empty state/error message
      } finally {
        setLoading(false); // Set loading false after fetch (success or failure)
      }
    };

    fetchProjects();
  }, [selectedTag, currentPage]); // Data fetching depends only on these state variables

  // Effect to update URL search params when selectedTag or currentPage state changes
  // This effect ensures the URL in the browser matches the component's state.
  useEffect(() => {
    const newParams = new URLSearchParams();
    newParams.append('page', currentPage.toString());
    if (selectedTag) {
      newParams.append('tag', selectedTag);
    }
    // Change: Removed { replace: true } to allow sequential back navigation.
    setSearchParams(newParams.toString());
  }, [currentPage, selectedTag, setSearchParams]);

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return; // Prevent invalid page numbers
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top on page change
  };

  const handleTagChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedTag(e.target.value);
    setCurrentPage(1); // Reset to first page on tag change
    window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top on tag change
  };

  if (loading) {
    return (
      <div className="project-list-container">
        <p className="loading-message">Loading projects...</p>
      </div>
    );
  }

  return (
    <div className="project-list-container">
      <h1>All Projects</h1>

      <div className="tag-filter-section">
        <label htmlFor="tag-select">Filter by Tag:</label>
        <select
          id="tag-select"
          value={selectedTag}
          onChange={handleTagChange}
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
              <Link
                to={`/projects/${project.id}`}
                className="project-card-link"
              >
                <h2>{project.title}</h2>
                {project.image && (
                  <img src={project.image} alt={project.title} />
                )}
                <p>
                  {/* Apply stripHtmlTags here before substring */}
                  {stripHtmlTags(project.description).substring(0, 150)}...
                </p>
                <div className="project-tags">
                  {project.tags &&
                    project.tags.map((tag, index) => (
                      <span key={index} className="tag-badge">
                        {tag}
                      </span>
                    ))}
                </div>
              </Link>
              <div className="project-card-actions">
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
          !loading && <p>No projects found matching the criteria.</p>
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
