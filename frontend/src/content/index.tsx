import axios from "axios";
import { Dispatch, ReactElement, SetStateAction, useCallback, useEffect, useState } from "react";

import JWTData from "schemas/jwtData";

import styles from "./index.module.scss";

type propsType = Readonly<{
    userData: JWTData,
    setLoading: Dispatch<SetStateAction<boolean>>
}>;

export default function Content(props: propsType): ReactElement {
    const {
        userData,
        setLoading
    } = props;

    const [status, setStatus] = useState<Array<boolean | undefined>>([]);
    const [resetStatus, setResetStatus] = useState<boolean | undefined>(undefined);
    const [queryStrings, setQueryStrings] = useState<Array<string | undefined>>([
        undefined,
        undefined,
        undefined
    ]);

    const resetDB = useCallback(() => {
        setLoading(true);
        axios.put("/reset").then(response => {
            const data = response.data as {
                success: boolean
            };
            setResetStatus(data.success);
        }).catch(() => {
            setResetStatus(false);
        }).finally(() => setLoading(false));
    }, [setLoading]);

    const updateStatus = useCallback(() => {
        axios.get("/check").then(response => {
            const data: Array<number> = response.data;
            setStatus(data.map(v => v === 1));
        })
    }, []);

    const checkTask = useCallback((index: number, queryStrings?: Array<string | undefined>) => {
        if (queryStrings && queryStrings.includes(undefined))
            return;

        setStatus(v => {
            const nv = Array.from(v);
            nv[index] = undefined;
            return nv;
        });
        axios.post(
            `/check/${index}`,
            {
                query_strings: queryStrings
            }
        ).catch(() => {
            alert(`Unexcept error while checking, please contact to TAs.`)
        }).finally(() => {
            setTimeout(updateStatus, 1000);
        })
    }, [updateStatus]);

    useEffect(() => {
        updateStatus();
    }, [updateStatus]);

    return <div className={styles.content}>
        <div className={styles.topBar}>
            <span className="ms">account_circle</span>
            <div>{userData.username.toUpperCase()}</div>
            <div className={styles.resetStatus}>
                {resetStatus === undefined ? "" :
                    resetStatus ? "Reset success!" : "Reset failed."}
            </div>
            <button onClick={resetDB}>Reset DB</button>
        </div>
        {
            Array.from(Array(4)).map((_, index) => <div
                key={index}
                className={styles.task}
            >
                <div
                    className={styles.status}
                    data-status={status[index]}
                >
                    {
                        status[index] === undefined ? "Loading" :
                            status[index] ? "Pass" : "Not Pass"
                    }
                </div>
                <h2>{`Task ${index + 1}`}</h2>
                <button
                    onClick={() => { index === 3 ? checkTask(index, queryStrings) : checkTask(index) }}
                    disabled={status[index] !== false || (index === 3 && (queryStrings.includes("") || queryStrings.includes(undefined)))}
                >Check</button>

                {index === 3 && status[index] !== true ? <div
                    className={styles.queryStrings}
                >
                    {Array.from(Array(3)).map((_, index) => <div
                        key={index}
                        className={styles.queryBox}
                        data-empty={queryStrings[index] === ""}
                    >
                        <span className="ms">{`counter_${index + 1}`}</span>
                        <input
                            type="text"
                            value={queryStrings[index]}
                            onChange={ev => setQueryStrings(v => {
                                const nv = Array.from(v);
                                nv[index] = ev.target.value;
                                return nv as [string, string, string];
                            })}
                        />
                    </div>)}
                </div> : undefined}
            </div>)
        }
    </div>
}