import { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';
import './css/ExperienceDetail.css';

interface ExperiencePhoto {
  id: string;
  image: string; // URL of the photo
  caption: string;
  display_order: number;
}

interface Experience {
  id: string;
  company_name: string;
  job_title: string;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  end_date_display: string;
  work_details: string; // This will now contain HTML
  photos: ExperiencePhoto[]; // Nested photos
}

const ExperienceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [experience, setExperience] = useState<Experience | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedPhoto, setSelectedPhoto] = useState<string | undefined>(undefined);

  useEffect(() => {
    const fetchExperience = async () => {
      if (!id) {
        setError('Experience ID not found in URL.');
        setLoading(false);
        return;
      }
      try {
        const response = await axios.get<Experience>(`${import.meta.env.VITE_API_URL}experiences/${id}/`);
        setExperience(response.data);
        if (response.data.photos && response.data.photos.length > 0) {
          setSelectedPhoto(response.data.photos[0].image); // Set first photo as default
        }
      } catch (err) {
        console.error('Failed to fetch experience details:', err);
        setError('Failed to load experience details.');
      } finally {
        setLoading(false);
      }
    };
    fetchExperience();
  }, [id]);

  if (loading) {
    return <div className="experience-detail-container"><p className="loading-message">Loading experience details...</p></div>;
  }

  if (error) {
    return <div className="experience-detail-container"><p className="error">{error}</p><Link to="/experience" className="btn secondary">Back to Experiences</Link></div>;
  }

  if (!experience) {
    return <div className="experience-detail-container"><p className="no-experience-found">Experience not found.</p><Link to="/experience" className="btn secondary">Back to Experiences</Link></div>;
  }

  return (
    <div className="experience-detail-container">
      <h1 className="company-name">{experience.company_name}</h1>
      <h2 className="job-title">{experience.job_title}</h2>
      <p className="experience-dates">
        {new Date(experience.start_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short' })} - {experience.end_date_display}
      </p>

      {experience.photos && experience.photos.length > 0 && (
        <div className="experience-photo-gallery">
          <div className="selected-photo-container">
            <img src={selectedPhoto || experience.photos[0].image} alt={experience.photos[0].caption || "Experience Photo"} className="selected-experience-photo" />
          </div>
          <div className="photo-thumbnails">
            {experience.photos.map((photo) => (
              <img
                key={photo.id}
                src={photo.image}
                alt={photo.caption}
                className={`thumbnail-experience-photo ${selectedPhoto === photo.image ? 'active' : ''}`}
                onClick={() => setSelectedPhoto(photo.image)}
              />
            ))}
          </div>
        </div>
      )}

      {/* REMOVED .replace(/\n/g, '<br/>') because work_details will now be HTML */}
      <div className="experience-details" dangerouslySetInnerHTML={{ __html: experience.work_details }} />

      <div className="back-link">
        <Link to="/experience" className="btn secondary">
          ← Back to Professional Experiences
        </Link>
      </div>
    </div>
  );
};

export default ExperienceDetail;
