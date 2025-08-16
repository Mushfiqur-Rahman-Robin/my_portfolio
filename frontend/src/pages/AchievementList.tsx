import { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom'; // 1. Import useSearchParams
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

const ACHIEVEMENTS_PER_PAGE = 3;

const AchievementList: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
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
    const fetchAchievements = async () => {
      setLoading(true);
      try {
        const response = await axios.get<PaginationInfo<Achievement>>(
          `${import.meta.env.VITE_API_URL}achievements/?page=${currentPage}&page_size=${ACHIEVEMENTS_PER_PAGE}`,
        );
        setAchievements(response.data.results);
        setTotalPages(Math.ceil(response.data.count / ACHIEVEMENTS_PER_PAGE));
        setError(null);
      } catch (err) {
        setError('Failed to fetch achievements.');
        console.error('Achievements fetch error:', err);
        setAchievements([]);
        setTotalPages(1);
      } finally {
        setLoading(false);
      }
    };
    fetchAchievements();
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
