import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './ExperienceList.css';

interface Experience {
  id: string;
  company_name: string;
  job_title: string;
  start_date: string;
  end_date_display: string; // From serializer method field
  work_details: string;
  is_current: boolean;
  display_order: number;
}

const ExperienceList: React.FC = () => {
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchExperiences = async () => {
      try {
        const response = await axios.get<Experience[]>(`${import.meta.env.VITE_API_URL}experiences/`);
        setExperiences(response.data);
      } catch (err) {
        setError("Failed to fetch professional experiences.");
        console.error("Experience fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchExperiences();
  }, []);

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
        {experiences.length > 0 ? (
          experiences.map((exp) => (
            <div key={exp.id} className="experience-card">
              <h2>{exp.company_name}</h2>
              <h3>{exp.job_title}</h3>
              <p className="experience-dates">
                {new Date(exp.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - {exp.end_date_display}
              </p>
              <p className="experience-details-preview">
                {exp.work_details.substring(0, 200)}... {/* Truncate for preview */}
              </p>
              <Link to={`/experience/${exp.id}`} className="btn secondary">
                View Details
              </Link>
            </div>
          ))
        ) : (
          <p>No professional experience found.</p>
        )}
      </div>
    </div>
  );
};

export default ExperienceList;
