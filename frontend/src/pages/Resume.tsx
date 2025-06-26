import { useState, useEffect } from 'react';
import axios from 'axios';
import './css/Resume.css';

interface ResumeFile {
  id: string;
  title: string;
  pdf_file: string; // Full URL to the PDF file
  uploaded_at: string;
}

const Resume: React.FC = () => {
  const [resume, setResume] = useState<ResumeFile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchResume = async () => {
      try {
        // Fetch the latest resume (assuming backend orders by uploaded_at desc)
        const response = await axios.get<ResumeFile[]>(`${import.meta.env.VITE_API_URL}resumes/`);
        if (response.data && response.data.length > 0) {
          setResume(response.data[0]); // Get the latest one
        } else {
          setError("No resume found. Please upload one via Django admin.");
        }
      } catch (err) {
        // This is where we might log more detailed network errors
        console.error("Resume fetch error:", err);
        if (axios.isAxiosError(err) && err.response) {
            setError(`Failed to fetch resume: ${err.response.status} ${err.response.statusText}. Ensure resume is uploaded and backend is serving media.`);
        } else {
            setError("Failed to fetch resume. Please check your network connection and backend status.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchResume();
  }, []);

  if (loading) {
    return (
      <div className="resume-container">
        <p className="loading-message">Loading resume...</p>
      </div>
    );
  }

  return (
    <div className="resume-container">
      <h1>My Resume</h1>
      {error && <p className="error">{error}</p>}
      {resume ? (
        <div className="resume-viewer">
          {/* Download button in the top right corner */}
          <a
            href={resume.pdf_file}
            download // Added download attribute
            target="_blank"
            rel="noopener noreferrer"
            className="download-pdf-button"
          >
            Download PDF
          </a>
          {/* Using iframe for PDF display */}
          <iframe
            src={resume.pdf_file}
            title={resume.title}
            width="100%"
            height="800px"
            style={{ border: 'none' }}
          >
            This browser does not support PDFs. Please download the PDF to view it:
            <a href={resume.pdf_file} target="_blank" rel="noopener noreferrer">
              Download Resume
            </a>
          </iframe>
          <p className="download-text">
            If the PDF does not load, you can{' '}
            <a href={resume.pdf_file} target="_blank" rel="noopener noreferrer">
              download it directly
            </a>
            .
          </p>
        </div>
      ) : (
        <p className="no-resume-found">
          {error || "No resume currently available. Please check back later."}
        </p>
      )}
    </div>
  );
};

export default Resume;
