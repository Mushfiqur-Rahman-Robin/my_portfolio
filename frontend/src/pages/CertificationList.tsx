import { useState, useEffect } from 'react';
import axios from 'axios';
import './css/ListPage.css';

interface Certification {
  id: string;
  name: string;
  issuing_organization: string;
  credential_url?: string;
  issue_date: string;
  image?: string;
  display_order: number;
}

interface PaginationInfo<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Define the number of items per page for this list view
const CERTIFICATIONS_PER_PAGE = 3; // <--- NEW CONSTANT

const CertificationList: React.FC = () => {
  const [certifications, setCertifications] = useState<Certification[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    const fetchCertifications = async () => {
      setLoading(true); // Start loading when page changes
      try {
        // Construct the URL with page and page_size parameters
        const response = await axios.get<PaginationInfo<Certification>>(
          `${import.meta.env.VITE_API_URL}certifications/?page=${currentPage}&page_size=${CERTIFICATIONS_PER_PAGE}`, // <--- ADDED page_size
        );
        setCertifications(response.data.results);
        // CRITICAL FIX: Calculate totalPages based on the new constant
        setTotalPages(Math.ceil(response.data.count / CERTIFICATIONS_PER_PAGE));
        setError(null); // Clear any previous errors
      } catch (err) {
        setError('Failed to fetch certifications.');
        console.error('Certifications fetch error:', err);
        setCertifications([]); // Ensure empty state on error
        setTotalPages(1); // Reset total pages on error
      } finally {
        setLoading(false);
      }
    };
    fetchCertifications();
  }, [currentPage]); // Re-fetch whenever currentPage changes

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="list-page-container">
        <p className="loading-message">Loading certifications...</p>
      </div>
    );
  }

  return (
    <div className="list-page-container">
      <h1>My Certifications</h1>
      {error && <p className="error">{error}</p>}
      <div className="items-grid">
        {certifications.length > 0 ? (
          certifications.map((cert) => (
            <div key={cert.id} className="list-card">
              <h2>{cert.name}</h2>
              <p className="item-organization">{cert.issuing_organization}</p>
              {cert.image && (
                <img src={cert.image} alt={cert.name} className="item-image" />
              )}
              <p className="item-date">
                Issued: {new Date(cert.issue_date).toLocaleDateString()}
              </p>
              {cert.credential_url && (
                <a
                  href={cert.credential_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn primary"
                >
                  View Credential
                </a>
              )}
            </div>
          ))
        ) : (
          <p>No certifications found.</p>
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

export default CertificationList;
