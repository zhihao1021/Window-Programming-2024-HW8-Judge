import axios from "axios";
import { Dispatch, ReactElement, SetStateAction, useCallback, useEffect, useState } from "react";

import JWT from "schemas/jwt";

import styles from "./index.module.scss";

type propsType = Readonly<{
    setLoading: Dispatch<SetStateAction<boolean>>,
    setToken: Dispatch<SetStateAction<string | null>>
}>;

export default function LoginBox(props: propsType): ReactElement {
    const {
        setLoading,
        setToken
    } = props;

    const [account, setAccount] = useState<string | null>(null);
    const [password, setPassword] = useState<string | null>(null);
    const [loginFailed, setLoginFailed] = useState<boolean>(false);

    const login = useCallback(() => {
        if (!(account && password)) {
            return;
        }

        setLoading(true);
        axios.post(
            "/auth",
            {
                sid: account,
                password: password
            }
        ).then(response => {
            const jwt: JWT = response.data;
            localStorage.setItem("token_type", jwt.token_type);
            localStorage.setItem("access_token", jwt.access_token);
            setToken(jwt.access_token);
        }).catch(() => {
            setPassword("");
            setLoginFailed(true);
        }).finally(() => {
            setLoading(false);
        })
    }, [account, password, setLoading, setToken]);

    useEffect(() => {
        if (account && password) {
            setLoginFailed(false);
        }
    }, [account, password])

    return <div className={styles.loginBox} onKeyDown={ev => {
        if (ev.key === "Enter") {
            login()
        }
    }}>
        <h1>Login</h1>
        <div className={styles.inputBox} data-empty={account === ""}>
            <span className="ms">account_circle</span>
            <input
                type="text"
                value={account ?? ""}
                onChange={ev => setAccount(ev.target.value)}
            />
        </div>
        <div className={styles.inputBox} data-empty={password === ""}>
            <span className="ms">password</span>
            <input
                type="password"
                value={password ?? ""}
                onChange={ev => setPassword(ev.target.value)}
            />
        </div>
        {loginFailed ? <div className={styles.loginFailed}>
            Wrong account or password!
        </div> : undefined}
        <button
            className={styles.login}
            disabled={!(password && account)}
            onClick={login}
        >Login</button>
    </div>;
};
