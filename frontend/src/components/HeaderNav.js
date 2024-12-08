import React from 'react';
import { Link } from 'react-router-dom';

function HeaderNav() {
  return (
    <div className="header">
      <nav>
        <Link to="/">Main</Link>
        <Link to="/stats">Stats</Link>
      </nav>
    </div>
  );
}

export default HeaderNav;
