import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Navbar from '../components/Navbar';

const renderNavbar = () =>
  render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>,
  );

describe('<Navbar />', () => {
  it('renders the brand logo and all primary navigation links', () => {
    renderNavbar();

    expect(screen.getByRole('link', { name: 'My Portfolio' })).toBeInTheDocument();

    const labels = [
      'Home',
      'About',
      'Projects',
      'Certifications',
      'Publications',
      'Achievements',
      'Experience',
      'Resume',
      'Contact',
    ];
    for (const label of labels) {
      expect(screen.getByRole('link', { name: label })).toBeInTheDocument();
    }
  });

  it('toggles the mobile menu open then closed via the hamburger control', async () => {
    renderNavbar();

    const hamburger = document.querySelector('.hamburger') as HTMLElement | null;
    expect(hamburger).not.toBeNull();

    const user = userEvent.setup();
    await user.click(hamburger!);
    expect(document.querySelector('.nav-menu.active')).not.toBeNull();

    await user.click(hamburger!);
    expect(document.querySelector('.nav-menu.active')).toBeNull();
  });

  it('turns off body scroll lock on unmount (cleanup)', () => {
    const { unmount } = renderNavbar();
    unmount();
    expect(document.body.classList.contains('mobile-menu-open')).toBe(false);
  });
});
