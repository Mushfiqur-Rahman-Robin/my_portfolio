import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom'; // 1. Import useSearchParams
import './css/ExperienceList.css';
import { stripHtmlTags } from '../utils/html_cleaner';

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

const EXPERIENCES_PER_PAGE = 2; // Define page size constant

const ExperienceList: React.FC = () => {
    const [experiences, setExperiences] = useState<Experience[]>([]);
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
        const fetchExperiences = async () => {
            setLoading(true);
            try {
                const response = await axios.get<PaginationInfo<Experience>>(
                    `${import.meta.env.VITE_API_URL}experiences/?page=${currentPage}&page_size=${EXPERIENCES_PER_PAGE}`
                );
                setExperiences(response.data.results);
                setTotalPages(Math.ceil(response.data.count / EXPERIENCES_PER_PAGE));
                setError(null);
            } catch (error: unknown) {
              let errorMessage = "Failed to fetch experiences: An unexpected error occurred.";
              if (axios.isAxiosError(error)) {
                errorMessage = `Failed to fetch experiences: ${error.message}`;
                console.error('Axios error fetching experiences:', error);
              } else if (error instanceof Error) {
                errorMessage = `Failed to fetch experiences: ${error.message}`;
                console.error('Generic JS error fetching experiences:', error);
              } else {
                console.error("Unexpected error during experience fetch:", error);
              }
              setError(errorMessage);
              setExperiences([]);
              setTotalPages(1);
            } finally {
                setLoading(false);
            }
        };

        fetchExperiences();
    }, [currentPage]);

    // 5. Update handlePageChange to modify the URL
    const handlePageChange = (newPage: number) => {
        if (newPage < 1 || newPage > totalPages) return;

        setCurrentPage(newPage); // Update state

        // Update the URL search parameter to create a history entry
        const newParams = new URLSearchParams(searchParams);
        newParams.set('page', newPage.toString());
        setSearchParams(newParams);
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
                            {stripHtmlTags(exp.work_details).substring(0, 200)}...
                        </p>
                        <Link to={`/experience/${exp.id}`} className="btn secondary">
                            View Details
                        </Link>
                    </div>
                ))}
            </div>

            <div className="pagination">
                <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="btn pagination-btn"
                >
                    Previous
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                    <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`btn pagination-btn ${currentPage === page ? 'active' : ''}`}
                    >
                        {page}
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
        </div>
    );
};

export default ExperienceList;
