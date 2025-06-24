import { useState, useEffect } from 'react';
import axios from 'axios';
import './ListPage.css';

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

const AchievementList: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);

  useEffect(() => {
    const fetchAchievements = async () => {
      try {
        const response = await axios.get<PaginationInfo<Achievement>>(
          `${import.meta.env.VITE_API_URL}achievements/?page=${currentPage}`,
        );
        setAchievements(response.data.results); // CRITICAL FIX: Access results array
        setTotalPages(Math.ceil(response.data.count / 6)); // Assuming 6 items per page
      } catch (err) {
        setError('Failed to fetch achievements.');
        console.error('Achievements fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAchievements();
  }, [currentPage]);

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
