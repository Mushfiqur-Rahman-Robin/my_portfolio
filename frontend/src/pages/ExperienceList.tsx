import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './css/ExperienceList.css';

interface Experience {
    id: string;
    company_name: string;
    job_title: string;
    start_date: string;
    end_date_display: string;
    work_details: string;
    is_current: boolean;
    display_order: number;
}

interface PaginationInfo<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

const ExperienceList: React.FC = () => {
    const [experiences, setExperiences] = useState<Experience[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [totalPages, setTotalPages] = useState<number>(1);

    useEffect(() => {
        const fetchExperiences = async () => {
            setLoading(true);
            try {
                // Correct URL with page parameter
                const response = await axios.get<PaginationInfo<Experience>>(
                    `${import.meta.env.VITE_API_URL}experiences/?page=${currentPage}`
                );
                // Update state with results and pagination info
                setExperiences(response.data.results);
                setTotalPages(Math.ceil(response.data.count / 2));  // items per page from backend
                setError(null);
            // } catch (err: any) {
            //     setError(`Failed to fetch experiences: ${err.message}`);
            //     console.error('Error fetching experiences:', err);
            //     setExperiences([]);  // Ensure empty state on error
            //     setTotalPages(1);
              } catch (error: unknown) {
              let errorMessage = "Failed to fetch experiences: An unexpected error occurred."; // Provide a default message
              if (axios.isAxiosError(error)) { // Check if it's an Axios error
                errorMessage = `Failed to fetch experiences: ${error.message}`;  // Now we are sure it has .message
                console.error('Axios error fetching experiences:', error);
              } else if (error instanceof Error) { // Standard JS error.
                errorMessage = `Failed to fetch experiences: ${error.message}`;
                console.error('Generic JS error fetching experiences:', error);
              } else {
                console.error("Unexpected error during experience fetch:", error); // Fallback if it's neither Axios nor standard error
              }
              setError(errorMessage);
              setExperiences([]);  // Ensure empty state on error
              setTotalPages(1);
            } finally {
                setLoading(false);
            }
        };

        fetchExperiences();
    }, [currentPage]);

    const handlePageChange = (newPage: number) => {
        setCurrentPage(newPage);
    };

    if (loading) {
        return (
            <div className="experience-list-container">
                <p className="loading-message">Loading experiences...</p>
            </div>
        );
    }

    return (
        <div className="experience-list-container">
            <h1>Professional Experience</h1>
            {error && <p className="error">{error}</p>}
            <div className="experiences-grid">
                {experiences.map((exp) => (
                    <div key={exp.id} className="experience-card">
                        <h2>{exp.company_name}</h2>
                        <h3>{exp.job_title}</h3>
                        <p className="experience-dates">
                            {new Date(exp.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - {exp.end_date_display}
                        </p>
                        <p className="experience-details-preview">
                            {exp.work_details.substring(0, 200)}...
                        </p>
                        <Link to={`/experience/${exp.id}`} className="btn secondary">
                            View Details
                        </Link>
                    </div>
                ))}
            </div>

            {/* Pagination Controls */}
            <div className="pagination">
                <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="btn pagination-btn"  // Use existing classes for style consistency
                >
                    Previous
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`btn pagination-btn ${currentPage === page ? 'active' : ''}`} // Use existing classes
                    >
                        {page}
                    </button>
                ))}
                <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="btn pagination-btn"  // Existing class to apply styles you have
                >
                    Next
                </button>
            </div>
        </div>
    );
};

export default ExperienceList;
