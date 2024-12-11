import ReactDOM from "react-dom/client";

import { setRequestConfig, setResponseConfig } from "config/axios";

import App from "./App";

import "./index.css";


declare module "react" {
  interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    // extends React's HTMLAttributes
    directory?: string;
    webkitdirectory?: string;
    mozdirectory?: string;
  }
};

setRequestConfig();
setResponseConfig();


const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <App />
);

