import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { userActions } from '_store';

export { Home };

function Home() {
    const dispatch = useDispatch();
    const { user: authUser } = useSelector(x => x.auth);

    return (
        <div>
            <h1>Hi {authUser?.userInfo.username}!</h1>
        </div>
    );
}
