import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="social-links">
          <a
            href="https://github.com/Mushfiqur-Rahman-Robin" // Replaced with your GitHub URL
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <a
            href="https://linkedin.com/in/mushfiqur--rahman" // Replaced with your LinkedIn URL
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
          <a
            href="https://facebook.com/your-facebook-profile" // New: Facebook
            target="_blank"
            rel="noopener noreferrer"
          >
            Facebook
          </a>
          <a
            href="https://www.instagram.com/your-instagram-profile" // New: Instagram (instead of Twitter)
            target="_blank"
            rel="noopener noreferrer"
          >
            Instagram
          </a>
          <a
            href="https://huggingface.co/your-huggingface-profile" // New: Hugging Face
            target="_blank"
            rel="noopener noreferrer"
          >
            Hugging Face
          </a>
          <a
            href="https://scholar.google.com/citations?user=your-google-scholar-id" // New: Google Scholar
            target="_blank"
            rel="noopener noreferrer"
          >
            Google Scholar
          </a>
        </div>
        <p>&copy; {new Date().getFullYear()} Md Mushfiqur Rahman. All rights reserved.</p> {/* Updated name */}
      </div>
    </footer>
  );
};

export default Footer;
