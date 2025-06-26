import './css/Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="social-links">
          <a
            href="https://github.com/Mushfiqur-Rahman-Robin"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
          <a
            href="https://www.linkedin.com/in/mushfiqur--rahman/"
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
          <a
            href="https://www.facebook.com/mushfiqur.rahman.78/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Facebook
          </a>
          <a
            href="https://www.instagram.com/mushfiqur._.rahman/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Instagram
          </a>
          <a
            href="https://huggingface.co/mushfiqurrobin"
            target="_blank"
            rel="noopener noreferrer"
          >
            Hugging Face
          </a>
          <a
            href="https://scholar.google.com/citations?user=2-Z5fHgAAAAJ"
            target="_blank"
            rel="noopener noreferrer"
          >
            Google Scholar
          </a>
        </div>
        <p>&copy; {new Date().getFullYear()} Md Mushfiqur Rahman. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
