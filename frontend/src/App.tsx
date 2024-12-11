import { jwtDecode } from "jwt-decode";
import { ReactElement, useMemo, useState } from "react";

import JWTData from "schemas/jwtData";

import LoadingPage from "loading";

import styles from "App.module.scss";
import LoginBox from "loginBox";
import Content from "content";

export default function App(): ReactElement {
    const [token, setToken] = useState<string | null>(localStorage.getItem("access_token"));
    const [loading, setLoading] = useState<boolean>(false);

    const userData: JWTData | null = useMemo(() => {
        if (token === null)
            return null;

        try {
            const data = jwtDecode(token) as JWTData;
            return data;
        }
        catch {
            localStorage.removeItem("access_token")
            return null;
        }
    }, [token]);

    return <div className={styles.app}>
        <LoadingPage show={loading} />
        {
            userData === null ? <LoginBox
                setLoading={setLoading}
                setToken={setToken}
            /> : <Content
                userData={userData}
                setLoading={setLoading}
            />
        }
    </div>
}