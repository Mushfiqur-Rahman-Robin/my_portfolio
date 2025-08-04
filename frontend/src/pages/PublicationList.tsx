import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom'; // 1. Import useSearchParams
import './css/ListPage.css';

interface Publication {
  id: string;
  title: string;
  authors: string;
  conference: string;
  publication_url: string;
  published_date: string;
  display_order: number;
}

interface PaginationInfo<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

const PUBLICATIONS_PER_PAGE = 3;

const PublicationList: React.FC = () => {
  const [publications, setPublications] = useState<Publication[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [totalPages, setTotalPages] = useState<number>(1);

  // 2. Initialize searchParams to manage URL state
  const [searchParams, setSearchParams] = useSearchParams();

  // 3. Initialize currentPage state from the URL, defaulting to 1
  const [currentPage, setCurrentPage] = useState<number>(() => {
    const page = searchParams.get('page');
    return page ? parseInt(page, 10) : 1;
  });

  // 4. Effect to sync state from URL (for back/forward buttons)
  useEffect(() => {
    const pageFromUrl = parseInt(searchParams.get('page') || '1', 10);
    if (currentPage !== pageFromUrl) {
      setCurrentPage(pageFromUrl);
    }
  }, [searchParams]);

  useEffect(() => {
    const fetchPublications = async () => {
      setLoading(true);
      try {
        const response = await axios.get<PaginationInfo<Publication>>(
          `${import.meta.env.VITE_API_URL}publications/?page=${currentPage}&page_size=${PUBLICATIONS_PER_PAGE}`,
        );
        setPublications(response.data.results);
        setTotalPages(Math.ceil(response.data.count / PUBLICATIONS_PER_PAGE));
        setError(null);
      } catch (err) {
        setError('Failed to fetch publications.');
        console.error('Publications fetch error:', err);
        setPublications([]);
        setTotalPages(1);
      } finally {
        setLoading(false);
      }
    };
    fetchPublications();
  }, [currentPage]);

  // 5. Update handlePageChange to modify the URL
  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;

    setCurrentPage(page); // Update state

    // Update the URL search parameter to create a history entry
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page.toString());
    setSearchParams(newParams);

    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="list-page-container">
        <p className="loading-message">Loading publications...</p>
      </div>
    );
  }

  return (
    <div className="list-page-container">
      <h1>My Publications</h1>
      {error && <p className="error">{error}</p>}
      <div className="items-grid">
        {publications.length > 0 ? (
          publications.map((pub) => (
            <div key={pub.id} className="list-card">
              <h2>{pub.title}</h2>
              <p className="item-authors">Authors: {pub.authors}</p>
              <p className="item-conference">Conference: {pub.conference}</p>
              <p className="item-date">
                Published: {new Date(pub.published_date).toLocaleDateString()}
              </p>
              <a
                href={pub.publication_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn primary"
              >
                View Publication
              </a>
            </div>
          ))
        ) : (
          <p>No publications found.</p>
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

export default PublicationList;
