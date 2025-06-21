import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  project_url?: string;
  repo_url?: string;
  tags: string;
  display_order: number;
  created_at: string;
}

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        // const response = await axios.get("http://localhost:8000/api/projects/");
        const response = await axios.get(`${import.meta.env.VITE_API_URL}projects/`);
        setProjects(response.data);
      } catch (err) {
        setError("Failed to fetch projects");
        console.error(err);
      }
    };
    fetchProjects();
  }, []);

  return (
    <>
      <h1>My Portfolio</h1>
      {error && <p className="error">{error}</p>}
      <div className="projects">
        {projects.length > 0 ? (
          projects.map((project) => (
            <div key={project.id} className="project-card">
              <h2>{project.title}</h2>
              <p>{project.description}</p>
              {project.image && <img src={project.image} alt={project.title} />}
              {project.project_url && (
                <a href={project.project_url} target="_blank" rel="noopener noreferrer">
                  View Project
                </a>
              )}
              {project.repo_url && (
                <a href={project.repo_url} target="_blank" rel="noopener noreferrer">
                  View Repository
                </a>
              )}
              <p>Tags: {project.tags}</p>
            </div>
          ))
        ) : (
          <p>No projects found.</p>
        )}
      </div>
    </>
  );
}

export default App;
