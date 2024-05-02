import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

import { history } from 'tools/history';

export const PrivateRoute = ({ children }) => {
    const { user: authUser } = useSelector(x => x.auth);
    
    if (!authUser) {
        // not logged in so redirect to login page with the return url
        return <Navigate to="/auth" state={{ from: history.location }} />
    }

    // authorized so return child components
    return children;
}