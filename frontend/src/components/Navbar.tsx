import { useState } from 'react';
import { Link } from 'react-router-dom';
import './css/Navbar.css';

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          My Portfolio
        </Link>

        <div className={`hamburger ${isMenuOpen ? 'active' : ''}`} onClick={toggleMenu}>
          <span></span>
          <span></span>
          <span></span>
        </div>

        <ul className={`nav-menu ${isMenuOpen ? 'active' : ''}`}>
          <li className="nav-item">
            <Link to="/" className="nav-links" onClick={closeMenu}>
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/about" className="nav-links" onClick={closeMenu}>
              About
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/projects" className="nav-links" onClick={closeMenu}>
              Projects
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/certifications" className="nav-links" onClick={closeMenu}>
              Certifications
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/publications" className="nav-links" onClick={closeMenu}>
              Publications
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/achievements" className="nav-links" onClick={closeMenu}>
              Achievements
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/experience" className="nav-links" onClick={closeMenu}>
              Experience
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/resume" className="nav-links" onClick={closeMenu}>
              Resume
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/contact" className="nav-links" onClick={closeMenu}>
              Contact
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
