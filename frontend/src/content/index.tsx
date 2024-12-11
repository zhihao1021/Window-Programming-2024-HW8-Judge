import { ReactElement, useCallback, useEffect, useState } from "react";

import styles from "./index.module.scss";
import axios from "axios";

export default function Content(): ReactElement {
    const [status, setStatus] = useState<Array<boolean | undefined>>([]);
    const [queryStrings, setQueryStrings] = useState<Array<string | undefined>>([
        undefined,
        undefined,
        undefined
    ]);

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