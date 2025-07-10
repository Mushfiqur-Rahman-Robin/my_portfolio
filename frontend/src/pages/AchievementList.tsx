import { useState, useEffect } from 'react';
import axios from 'axios';
import './css/ListPage.css';

interface Achievement {
  id: string;
  title: string;
  description: string;
  date: string;
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
const ACHIEVEMENTS_PER_PAGE = 3; // <--- NEW CONSTANT

const AchievementList: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    const fetchAchievements = async () => {
      setLoading(true); // Start loading when page changes
      try {
        // Construct the URL with page and page_size parameters
        const response = await axios.get<PaginationInfo<Achievement>>(
          `${import.meta.env.VITE_API_URL}achievements/?page=${currentPage}&page_size=${ACHIEVEMENTS_PER_PAGE}`, // <--- ADDED page_size
        );
        setAchievements(response.data.results);
        // CRITICAL FIX: Calculate totalPages based on the new constant
        setTotalPages(Math.ceil(response.data.count / ACHIEVEMENTS_PER_PAGE));
        setError(null); // Clear any previous errors
      } catch (err) {
        setError('Failed to fetch achievements.');
        console.error('Achievements fetch error:', err);
        setAchievements([]); // Ensure empty state on error
        setTotalPages(1); // Reset total pages on error
      } finally {
        setLoading(false);
      }
    };
    fetchAchievements();
  }, [currentPage]); // Re-fetch whenever currentPage changes

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="list-page-container">
        <p className="loading-message">Loading achievements...</p>
      </div>
    );
  }

  return (
    <div className="list-page-container">
      <h1>My Achievements</h1>
      {error && <p className="error">{error}</p>}
      <div className="items-grid">
        {achievements.length > 0 ? (
          achievements.map((ach) => (
            <div key={ach.id} className="list-card">
              <h2>{ach.title}</h2>
              {ach.image && (
                <img src={ach.image} alt={ach.title} className="item-image" />
              )}
              <p className="item-description">{ach.description}</p>
              <p className="item-date">
                Date: {new Date(ach.date).toLocaleDateString()}
              </p>
            </div>
          ))
        ) : (
          <p>No achievements found.</p>
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

export default AchievementList;
