import { ReactElement } from "react";

import style from "./index.module.scss";


type propsType = Readonly<{
    show: boolean
}>;

export default function LoadingPage(props: propsType): ReactElement {
    const {
        show
    } = props;

    return <div className={style.loadingPage} data-show={show}>
        <div className={style.box}>
            <div className={style.left} />
            <div className={style.main}>
                <div>Loading...</div>
            </div>
            <div className={style.right} />
        </div>
    </div>
};
