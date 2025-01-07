import React, { lazy } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

// Lazy loading
const Home = lazy(() => import('./pages/Home/Home'));
const NotFound = lazy(() => import('./pages/404/NotFound'));

function App() {
  return (
    <React.Fragment>
      <Router>
        <React.Suspense fallback={<div>Loading...</div>}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<Navigate replace to="/404" />} />
          </Routes>
        </React.Suspense>
      </Router>
    </React.Fragment>
  );
}

export default App;
