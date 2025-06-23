import { useState, useEffect } from 'react';
import axios from 'axios';
import './Resume.css';

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
        // Adjust this if your backend uses a different way to get the "active" resume
        const response = await axios.get<ResumeFile[]>(`${import.meta.env.VITE_API_URL}resumes/`);
        if (response.data && response.data.length > 0) {
          // Assuming the latest resume is the first one if sorted by uploaded_at descending
          setResume(response.data[0]);
        } else {
          setError("No resume found. Please upload one via Django admin.");
        }
      } catch (err) {
        setError("Failed to fetch resume. Please check the API and ensure a resume is uploaded.");
        console.error("Resume fetch error:", err);
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
            download
            target="_blank"
            rel="noopener noreferrer"
            className="download-pdf-button" // New class for styling
          >
            Download PDF
          </a>
          {/* Using iframe for PDF display */}
          <iframe
            src={resume.pdf_file}
            title={resume.title}
            width="100%"
            height="800px" // Adjust height as needed
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
